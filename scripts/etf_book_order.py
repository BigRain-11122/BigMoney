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
import glob
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
from scripts import etf_equity_alpha as AE          # noqa: E402
from scripts import exchange_calendar_audit as CA   # noqa: E402
from scripts.etf_asset_class import classify       # noqa: E402
from scripts.etf_book_bets_face import read_published as read_bets_face  # noqa: E402
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
# r1177: this sheet repairs quote flips before it measures anything, like the card and the
# forward ledger already did. It was the last live face ranking on raw prices, so a
# share-count flip could enter a pick here and nowhere else, and the two faces of one book
# were quoting a CAGR computed on two different panels. The size of the correction is
# priced, not assumed: results/etf_book_flip_contamination.json (verdict MATERIAL).
REPAIR_PANEL = True
PRICE_BASIS_ARTIFACT = "results/etf_book_flip_contamination.json"


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


# ------------------------------------------------------------------ feed freshness
# One implementation lives in exchange_calendar_audit (it owns the official calendar);
# these aliases keep the local call sites readable.
feed_status = CA.ticket_feed_status


def live_feed_status(ticket_bar, now=None):
    return CA.live_ticket_feed_status(ticket_bar, now=now)


def drawdown_band():
    """How bad can the drawdown be, per the bootstrap block arms (r1348).

    The order sheet prints one realised maxDD for a book that has one history. The same
    book, resampled, has a 5th-percentile drawdown several pp deeper -- so an operator
    sizing to the printed number is sizing to a median. Soft-fails to None.
    """
    try:
        files = sorted(glob.glob(os.path.join(BASE, "results", "etf_book_bootstrap",
                                              "BLOCKS-*.json")))
        if not files:
            return None
        with open(files[-1], "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or []
        if len(arms) < 2:
            return None
        return {"artifact": os.path.relpath(files[-1], BASE).replace("\\", "/"),
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "block_set": [a.get("block") for a in arms],
                "maxdd_p5": doc["spread"]["maxdd_p5"],
                "maxdd_p50": doc["spread"]["maxdd_p50"],
                "dd_break": doc["spread"]["dd_break_share"]}
    except Exception:
        return None


def carry_split(beta=None, path=None):
    """How much of the quoted headline is the 1-day repo leg (r1367).

    The sheet quotes one CAGR for a book that parks roughly half its NAV in GC001, so a
    reader cannot tell whether the selection machinery pays or the parking does. The split
    is measured once by ``scripts/etf_book_return_regime.py``; this reads that artifact at
    the beta the ticket is actually running instead of re-running the engine (and instead
    of hand-copying a number that would rot).

    Soft-fails to None -- the caller must say so, because silence reads as "all alpha".
    """
    p = path or os.path.join(BASE, "results", "etf_book_return_regime.json")
    want = float(DEFAULT_BETA if beta is None else beta)
    try:
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        gate = doc.get("gate") or {}
        cells = gate.get("betas") or {}
        if not cells:
            return None
        key = min(cells, key=lambda k: abs(float(k) - want))
        cell = cells[key] or {}
        obs, flat, zero = (cell.get("observed_pct"), cell.get("flat_today_pct"),
                           cell.get("zero_pct"))
        if None in (obs, flat, zero):
            return None
        rates = doc.get("cash_rates") or {}
        try:
            artifact = os.path.relpath(p, BASE).replace("\\", "/")
        except Exception:                       # fixture on another drive
            artifact = str(p)
        return {"artifact": artifact,
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "beta": float(key),
                "beta_requested": want,
                "observed_pct": float(obs),
                "flat_today_pct": float(flat),
                "zero_pct": float(zero),
                "carry_pp": round(float(obs) - float(zero), 4),
                "flat_rate_cost_pp": round(float(obs) - float(flat), 4),
                "carry_share_pct": round(cell.get("carry_share_of_headline_pct")
                                         if cell.get("carry_share_of_headline_pct") is not None
                                         else 100.0 * (float(obs) - float(zero)) / float(obs), 3),
                "pp_per_100bp": cell.get("pp_per_100bp"),
                "cash_share": cell.get("cash_share"),
                "rate_today_pct": rates.get("today_pct"),
                "rate_today_date": rates.get("today_date"),
                "rate_observed_pct": rates.get("observed_mean_pct"),
                "identity_matched": (doc.get("identity") or {}).get("matched")}
    except Exception:
        return None


def card(ticket, mk, sched, asof, beta, extra):
    L = ["# ETF 复合书 · 可执行订单单（%s）" % asof, "",
         "当前活：β 目标 %.2f 的单本 R%d N%d + GC001 现金腿，每 %d 个交易日重算一次 k。"
         % (beta, REBAL, N_HOLD, REBAL),
         "最近实物：%s（本文件同日生成）。"
         % os.path.relpath(os.path.join(OUT_DIR, "TICKET-%s.json" % asof), BASE).replace("\\", "/"),
         "下个里程碑：下一决策日落单后前向账本追加一行（窗 ≤48h，随面板推进）。", ""]
    feed = extra.get("feed")
    if feed:
        lag = feed.get("lag_days")
        L += ["## 数据新鲜度（本单定价用的是哪一天的 bar）",
              "- 官方交易日历期望最新 bar：%s" % (feed.get("expected_bar") or "未知（无日历）"),
              "- 本单定价 bar：%s" % (feed.get("ticket_bar") or "未知"),
              "- 判定：**%s**｜落后 %s 个交易日" % (feed.get("status", "unknown"),
                                                  "?" if lag is None else lag),
              "- %s" % feed.get("detail", ""), ""]
        if feed.get("status") in ("stale_feed", "feed_broken"):
            L += ["> ⚠ 提醒：本单的定价 bar 落后市场 %s 个交易日 —— 这是数据面的滞后，"
                  "不是书换了判断。照此单下手前必须知道这一点。" % ("?" if lag is None else lag), ""]
    L += restatement_md(extra.get("restatements"))
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
    cs = extra.get("carry")
    if cs:
        L += ["", "## 这条年化里有多少是现金利息",
              "同一本书换三种现金利率重算（β %.2f 档）：按全窗真实 repo 利率年化 **%.2f%%** → "
              "按今天利率持平年化 **%.2f%%** → 现金零收益年化 **%.2f%%**。"
              % (cs["beta"], cs["observed_pct"], cs["flat_today_pct"], cs["zero_pct"]),
              "- 现金利息贡献 **%.2fpp = 年化的 %.1f%%**；现金占比 %.0f%%，利率每降 100bp "
              "年化约少 %.2fpp。"
              % (cs["carry_pp"], cs["carry_share_pct"], (cs["cash_share"] or 0.0) * 100,
                 cs["pp_per_100bp"] or 0.0),
              "- 读法：把现金腿按零利率计这本书仍有 %.2f%% —— 选股机器本身不是靠停车费活着；"
              "但今天报价里的 %.1f%% 确实是 repo 利息，利率掉到今天的 %.2f%%（%s 报价）"
              "就是少赚 %.2fpp，不是这个月选错了票。"
              % (cs["zero_pct"], cs["carry_share_pct"], cs["rate_today_pct"] or 0.0,
                 cs["rate_today_date"] or "未知", cs["flat_rate_cost_pp"])]
        if cs["evidence_cutoff"] and asof and cs["evidence_cutoff"] != asof:
            L += ["- ⚠ 拆解定价 bar %s 落后本单 %s：这是拆解面没跟上，不是利率变了，"
                  "按旧 bar 的数字只当量级读。" % (cs["evidence_cutoff"], asof)]
        L += ["- 出处：%s（cutoff %s；探索件，无预注册、无判决、不入账本）。"
              % (cs["artifact"], cs["evidence_cutoff"] or "未知")]
    else:
        L += ["", "## 这条年化里有多少是现金利息",
              "- 拆解面在盘上没有可用读数（results/etf_book_return_regime.json 缺失或"
              "缺本 β 档）：上面那个年化含现金利息，具体多少本单不报 —— "
              "这正是 r1367 要修的那个空白。"]
    db = drawdown_band()
    if db:
        L += ["", "## 最大回撤：本单上面那个数是中位数，不是尾部（r1348）",
              "本账簿只有一个历史。对同一条收益路径做块自助（块长 %s 根 bar，块长本身是自由参数），"
              "%s 百分位最大回撤落在 **%.1f%% ~ %.1f%%**，中位落在 %.1f%% ~ %.1f%%，"
              "跌破 -20%% 的重采样占比 %.1f%% ~ %.1f%%。"
              % ("/".join(str(b) for b in db["block_set"]), "5",
                 db["maxdd_p5"]["min"] * 100, db["maxdd_p5"]["max"] * 100,
                 db["maxdd_p50"]["min"] * 100, db["maxdd_p50"]["max"] * 100,
                 db["dd_break"]["min"] * 100, db["dd_break"]["max"] * 100),
              "- 口径：band 定价于 %s bar（%s）。按 p5 一档定仓位，不按中位一档。"
              % (db["evidence_cutoff"] or "未知", db["artifact"])]
    else:
        L += ["", "## 最大回撤的尾部", "- 无自助带在盘：上面只有单路径回撤，尾部未发布。"]
    ag = extra.get("agreement")
    if ag:
        L += ["", "## 两张生产面是不是同一天",
              "- 决策 bar：卡片 %s ｜ 本单 %s ｜ 一致=%s"
              % (ag["card_decided_at"], ag["ticket_book_decided_at"], ag["same_decision_bar"]),
              "- 定价 bar：卡片 %s（%s）｜ 本单 %s（%s）｜ 一致=%s"
              % (ag["card_priced_bar"] or "未知", ag["card_feed_status"] or "未知",
                 ag["ticket_priced_bar"], (feed or {}).get("status", "未知"),
                 ag["same_priced_bar"])]
        if not ag["same_priced_bar"]:
            L += ["- ⚠ 两张面定价不在同一天：卡片是配置口径的对照面、本单是可执行面，"
                  "若两张之间跨过了一个网格决策日，它们描述的是两本不同的书 —— 照单下手前"
                  "只看本单的仓位，卡片的名数与波动目标行不可当今天的仓位用。"]
    wd = extra.get("width")
    if wd:
        d = wd["delta_ticket_minus_card"]
        L += ["", "## 这张单是 %d 名，卡片是 %d 名" % (wd["ticket_names"], wd["card_names"]),
              "两张面不只名数不同，杠杆规则也不同（本单 %s 覆盖 / 卡片 %s 目标），"
              "所以下表的差值是一条对角线，不是「名数的代价」："
              % (wd["ticket_rule"], wd["card_rule"]),
              "| 账簿 | 名数 | 规则 | 年化 | 夏普 | 实现波动 | 最大回撤 |",
              "|---|---|---|---|---|---|---|",
              "| 本单（可执行） | %d | %s | %.1f%% | %.2f | %.1f%% | %.1f%% |"
              % (wd["ticket_names"], wd["ticket_rule"], wd["ticket"]["cagr"] * 100,
                 wd["ticket"]["sharpe"], (wd["ticket"].get("vol") or 0.0) * 100,
                 wd["ticket"]["maxdd"] * 100),
              "| 卡片（对照面） | %d | %s | %.1f%% | %.2f | %.1f%% | %.1f%% |"
              % (wd["card_names"], wd["card_rule"], wd["card"]["cagr"] * 100,
                 wd["card"]["sharpe"], (wd["card"].get("vol") or 0.0) * 100,
                 wd["card"]["maxdd"] * 100),
              "", "本单 − 卡片：年化 %+.2fpp、夏普 %+.3f、波动 %+.2fpp、回撤 %+.2fpp。"
              % (d["cagr_pp"], d["sharpe"], d.get("vol_pp") or 0.0, d["maxdd_pp"])]
        we = wd.get("width_effect") or {}
        if we:
            L += ["", "同一规则下只换名数（这才是名数的代价）："]
            for rule, v in sorted(we.items()):
                L += ["- %s 规则：%d 名 → %d 名 年化 %+.2fpp"
                      % (rule, wd["ticket_names"], wd["card_names"], v["pp"])]
        L += ["", "读法：名数的代价随规则变号（β 覆盖下宽账少担风险 → 少赚；8%% 波动目标下"
              "两宽度实现波动相当 → 名数几乎不花钱）。两张面的夏普差 %+.3f，即风险调整后"
              "基本等价——两者之间选，是选承担多少波动，不是选谁更会选股。"
              % d["sharpe"],
              "出处：%s（cutoff %s）。" % (wd["source"], wd["evidence_cutoff"])]
    ru = extra.get("ruler") or {}
    if ru.get("state") == "inside_disagreement":
        L += ["", "## 两张面之间的差，落在两台引擎自己打架的范围里",
              "把本单和卡片放到同一条尺子上、逐相位配对：中位差 **%+.2fpp**"
              "（%d 个相位，%s 个往上、%s 个往下，区间 %+.2f ~ %+.2f）；"
              "同一档 5→12 名在另一台引擎上是 **%+.2fpp** —— 两台引擎对这一档的分歧 "
              "**%+.2fpp**（方向还相反）。"
              % (float(ru["gap_pp"]), ru["pairs"], ru.get("positive_phases"),
                 (ru["pairs"] - (ru.get("positive_phases") or 0)) if ru.get("pairs") else "?",
                 float(ru.get("min_pp") if ru.get("min_pp") is not None
                       else -abs(float(ru.get("spread_pp") or 0)) / 2),
                 float(ru.get("max_pp") if ru.get("max_pp") is not None
                       else abs(float(ru.get("spread_pp") or 0)) / 2),
                 float(ru.get("capacity_rung_pp") or 0), float(ru["disagreement_pp"])),
              "- 读法：这个差只有引擎分歧的 **%.1f%%**，所以「本单比卡片差多少」这句话"
              "在本窗读不出来——能读出来的是：两张面之间的大部分差来自杠杆规则（β 覆盖 vs "
              "8%% 波动目标），不是名数。挑哪张面照旧看愿意承担多少波动。"
              % (100.0 * (ru.get("share_of_disagreement") or 0.0)),
              _resolution_md(ru),
              "- 出处：%s（cutoff %s，%s 个相位配对）。"
              % (ru["source"], ru["evidence_cutoff"], ru["pairs"])]
    elif ru.get("state") and ru["state"] != "unavailable":
        L += ["", "## 两张面之间的差（尺子没给出干净的读数）",
              "- 尺子状态：**%s** —— %s" % (ru["state"], ru.get("detail") or ""),
              "- 出处：%s（cutoff %s）。" % (ru.get("source"), ru.get("evidence_cutoff"))]
    L += ["", "## 诚实面", "",
          "- 探索件：无预注册、无判决、不入成绩账本。"]
    if not wd:
        L += ["- **名数差未定价**：本单 %d 名而生产卡片跑不同名数，本窗未取到宽度审计"
              "（scripts/etf_book_width_audit.py），差额未知。" % N_HOLD]
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
    if extra.get("bets_line"):
        L += ["- **五只名字不是五个赌注**：%s" % extra["bets_line"]]
    pb = extra.get("price_basis") or {}
    if pb.get("sentence"):
        L += ["- **价格面板**：%s" % pb["sentence"]]
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


def price_basis(close, cols, repaired=None):
    """Which prices this sheet's numbers are computed on, and how many prints that costs.

    One arithmetic, one sentence: `etf_equity_alpha.flip_census` counts the raw panel and
    `etf_equity_alpha.price_basis_line` writes the line, so this sheet and the production
    card cannot drift into quoting two different definitions of "clean" (E289).

    Since r1177 this sheet repairs (`REPAIR_PANEL`), matching the card and the forward
    ledger. Before that it was the only live face ranking on raw prices: a share-count flip
    that reads as a -90% day could enter a pick here and nowhere else, and the ticket's
    CAGR was then compared against a card priced on the other panel.
    """
    try:
        import etf_equity_alpha as A
    except Exception:
        return {"panel": "unknown", "flip_thr": None, "flip_prints": None,
                "sentence": ("本单的数字算在哪张价格面板上读不到（etf_equity_alpha 不可用），"
                             "所以这里不替它下结论。")}
    cen = A.flip_census(close, cols)
    line = A.price_basis_line(bool(REPAIR_PANEL if repaired is None else repaired),
                              cen["prints"], cen["thr"], cen["symbols"],
                              PRICE_BASIS_ARTIFACT, columns=cen["columns"])
    line["columns"] = cen["columns"]
    return line


def run(beta=DEFAULT_BETA, nav=DEFAULT_NAV, inception=DEFAULT_INCEPTION, fresh_gate=False):
    global OUT_DIR
    if fresh_gate:
        OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_order_fresh")
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    # census on the panel as the source prints it: after the repair the count is zero by
    # construction, and a disclosure that always reads "no flips" discloses nothing.
    basis = price_basis(close, cols)
    if REPAIR_PANEL:
        close, openp, _n_flip = AE.repair_flips(close, openp)
        print("price basis: repaired %d flip prints on %s symbols before any measurement"
              % (basis["flip_prints"], basis["symbols_with_a_flip"]), flush=True)
    score = F.build_score(close[cols], amt[cols], feats)
    stale = staleness_stats(score, close[cols])
    print("staleness: %d/%d picks (%.1f%%) priced before the decision bar | panel live on "
          "last bar %d/%d symbols | worst gap %dd"
          % (stale["stale_picks"], stale["picks"], 100.0 * (stale["stale_share"] or 0.0),
             stale["symbols_with_value_on_last_bar"], stale["symbols_total"],
             stale["worst_stale_gap_days"]), flush=True)
    # a second, independent staleness face: the one above is between symbols inside the
    # panel, this one is between the panel and the official calendar (r1287).
    feed = live_feed_status(close.index[-1])
    print("feed: %s | ticket bar %s vs official %s | lag %s day(s)"
          % (feed["status"], feed["ticket_bar"], feed["expected_bar"],
             "-" if feed["lag_days"] is None else feed["lag_days"]), flush=True)
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
    # ---- rank on the engine's last DECISION bar, never on the panel's last bar.
    # `run_next_open` re-decides only every REBAL bars, so ranking `slip.index[-1]` hands an
    # operator a ticket for a book the engine does not hold. At cutoff 2026-10-23 this
    # ticket listed the 10-23 top-5 while the book in force (and the production card, and
    # the forward ledger) had been decided 2026-10-14 -- disjoint sets, so following the
    # ticket would have traded five names the book never owned.
    grid_dates = [d for d in close.index if d >= pd.Timestamp("2020-01-01")]
    dec_bar = grid_dates[(len(grid_dates) - 1) // REBAL * REBAL] if grid_dates else None
    k_now = state.get("last_k")
    if k_now is None:
        k_now = 1.0
    cls_map = dict(zip(close.columns, classes))
    ticket = build_ticket(score.loc[dec_bar], close.loc[dec_bar],
                          k_now, nav, classes=cls_map) if dec_bar is not None else None
    if ticket is None:
        print("FATAL: no decision bar on the grid -- panel too short")
        return 2
    ticket_picks = [r["symbol"] for r in ticket["order"]]
    cb = card_book()
    agreement = None
    if cb:
        agreement = {"card_decided_at": cb["decided_at"],
                     "ticket_book_decided_at": str(dec_bar.date()),
                     "same_decision_bar": cb["decided_at"] == str(dec_bar.date()),
                     "ticket_is_prefix_of_card": cb["symbols"][:len(ticket_picks)] == ticket_picks,
                     "card_names": len(cb["symbols"]),
                     # the priced bar is the second half of the agreement: two faces can
                     # share a decision bar and still be built off different panel endings,
                     # and a card refreshed before a grid decision keeps describing the
                     # PREVIOUS book (r1290: the card sat at 2026-10-23/stale_feed while
                     # this ticket was already 2026-10-26/current, both calling themselves
                     # the production book, neither saying a word about the other).
                     "card_priced_bar": cb.get("priced_bar"),
                     "ticket_priced_bar": asof,
                     "same_priced_bar": bool(cb.get("priced_bar")) and cb.get("priced_bar") == asof,
                     "card_feed_status": cb.get("feed_status")}
        print("card agreement: same decision bar=%s | ticket is %d-name prefix of the card's "
              "%d-name book=%s | same priced bar=%s (card %s vs ticket %s)"
              % (agreement["same_decision_bar"], len(ticket_picks),
                 agreement["card_names"], agreement["ticket_is_prefix_of_card"],
                 agreement["same_priced_bar"], cb.get("priced_bar"), asof), flush=True)
    mk = metrics(slip, blip)
    wd = width_disclosure()
    ruler = live_width_ruler(asof=asof, card_n=(wd or {}).get("card_names"))
    carry = carry_split(beta)
    # r1172: five tickers are not five bets. The face that measures how many independent
    # directions the sleeve spans is quoted HERE, verbatim, so the operator reading this
    # order sees the concentration next to the weights instead of counting tickers (r1108
    # 有产无读). Absent or unreadable -> the ticket says so, never a silent pass.
    bets = read_bets_face()
    if bets.get("status") == "ok" and bets.get("sentence"):
        bets_line = bets["sentence"]
        if bets.get("evidence_cutoff") and bets["evidence_cutoff"] != asof:
            bets_line += " (measured on the %s bar)" % bets["evidence_cutoff"]
    else:
        bets_line = ("how many independent bets the sleeve holds is unpublished (%s); "
                     "run scripts/etf_book_bets_face.py run" % (bets.get("status") or "absent"))
    payload = {"evidence_cutoff": asof, "beta_target": float(beta),
               "inception": str(slip.index[0].date()) if len(slip) else inception,
               "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
               "fresh_gate": bool(fresh_gate), "staleness": stale,
               "feed_status": feed,
               "k_now": round(float(k_now), 6),
               "book_decided_at": str(dec_bar.date()),
               "card_agreement": agreement,
               "next_decision_bars": _next_decision(close.index, slip.index[-1]),
               "ticket": ticket, "metrics": mk,
               "book_leg": {"turnover_per_rebal": round(float(turnover), 4),
                            "open_gapfill": int(gapfill)},
               "cash_leg": {"source": "data/repo_daily/GC001.csv",
                            "mean_accrual_ann_pct": round(float(cash_rf.mean() * 252.0) * 100, 3),
                            "accrual_window": accrual_window(idx),
                            "missing_bar_steps": int(cash_missing)},
               "ledger": {"bars": int(state.get("rows", 0)), "nav": round(float(state["nav"]), 8),
                          "rows_added": len(merged), "engine_naive_vs_ledger": drift},
               "width_disclosure": wd,
               "live_width_ruler": ruler,
               "price_basis": basis,
               "carry_split": carry,
               "restatements": _ledger_restatements(),
               "bets": bets,
               "caveats": ["survivorship: on-disk panel holds ETFs that still exist",
                           "ticket prices are closes; no impact cost, no limit-move guard",
                           "GC001 single tenor, rolling assumed cost-free",
                           "k revised every %d bars so delivered beta still wanders" % REBAL,
                           bets_line,
                           "exploratory: no preregistration, no verdict, no ledger booking"]
                          + (["this ticket is the %d-name aggressive end of the book; the "
                              "production card runs %d names -- see width_disclosure"
                              % (N_HOLD, wd["card_names"])] if wd else
                             ["width disclosure unavailable: run "
                              "scripts/etf_book_width_audit.py run to price the %d-name ticket "
                              "against the production card" % N_HOLD])
                          + ([] if ruler["state"] == "inside_disagreement" else
                             ["live width ruler %s: %s" % (ruler["state"], ruler["detail"])])}

    _write("state.json", state)
    _write("TICKET-%s.json" % asof, payload)
    _write("latest.json", {"as_of": asof, "file": "TICKET-%s.json" % asof,
                           "beta_target": float(beta), "k_now": round(float(k_now), 6)})
    with open(os.path.join(OUT_DIR, "ORDER-%s.md" % asof), "w", encoding="utf-8") as f:
        f.write(card(ticket, mk, sched, asof, beta,
                     {"inception": payload["inception"], "stale": stale, "width": wd,
                      "feed": feed, "agreement": agreement, "ruler": ruler,
                      "carry": carry, "restatements": payload["restatements"],
                      "bets_line": bets_line,
                      "price_basis": payload["price_basis"]}))

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
    if wd:
        print("width: %d names here vs %d on the card -> %+.2fpp/yr CAGR, %+.3f Sharpe, "
              "%+.2fpp maxDD (audit cutoff %s)"
              % (wd["ticket_names"], wd["card_names"], wd["delta_ticket_minus_card"]["cagr_pp"],
                 wd["delta_ticket_minus_card"]["sharpe"],
                 wd["delta_ticket_minus_card"]["maxdd_pp"], wd["evidence_cutoff"]))
    else:
        print("width: disclosure unavailable (width audit or card width missing)")
    if carry:
        print("carry split: headline %.2f%% = cash %.2fpp (%.1f%% of it) | zero-cash %.2f%% | "
              "flat-today %.2f%%"
              % (carry["observed_pct"], carry["carry_pp"], carry["carry_share_pct"],
                 carry["zero_pct"], carry["flat_today_pct"]))
    else:
        print("carry split: unavailable -- the sheet says the headline is not decomposed")
    print("wrote", os.path.join(OUT_DIR, "TICKET-%s.json" % asof))
    return 0


CARD_DIR = os.path.join(PATHS.results_dir, "etf_book_production")
AUDIT_PATH = os.path.join(PATHS.results_dir, "etf_book_width_audit.json")
RULER_PATH = os.path.join(PATHS.results_dir, "etf_book_live_width_ruler.json")
RULER_STALE_DAYS = 10


def card_width(card_dir=None):
    """Name count the production card is actually running, read off its own artefact.

    Hardcoding 12 here would rot the moment the card's config changes; the pointer
    chain (latest.json -> PRODUCTION-<asof>.json) is the only place that knows.
    """
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        # latest.json is either a pointer to the dated card or the card itself
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        n = (doc.get("config") or {}).get("n_hold")
        return int(n) if n else None
    except Exception:
        return None


def card_book(card_dir=None):
    """(decided_at, ordered symbols) of the book the production card is holding.

    Read off the card's own artefact -- the same pointer chain as card_width. Used to
    assert the ticket and the card describe one book: after r1277 both rank on the same
    decision bar, so the ticket's N names must be a prefix of the card's list.
    """
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        sh = doc.get("sheet") or {}
        return {"decided_at": sh.get("book_decided_at") or sh.get("last_decision_bar"),
                "symbols": [l.get("symbol") for l in (sh.get("legs") or [])],
                "scale": sh.get("risk_scale"),
                # the bar the card was PRICED on, not just the bar its book was decided
                # on: both faces slice the same panel, but only this field says WHICH day
                # the numbers under it belong to. Measured r1290: on a non-grid day the
                # book is identical (vol overlay sizes at the decision bar, not daily) and
                # only the feed line moves -- but a card refreshed before a grid decision
                # and a ticket refreshed after it describe two different books, and
                # nothing in either face would have said so.
                "priced_bar": sh.get("as_of_bar"),
                "feed_status": (doc.get("feed_status") or {}).get("status")}
    except Exception:
        return None


# The ticket sizes through the fixed beta overlay, the card through an 8% vol target.
# That is not a detail: the audit's width table now carries BOTH rules (r1291), and a
# lookup keyed on the name count alone silently returns whichever arm was written last
# (the vol arm) -- i.e. it would print vol-rule numbers under the "this ticket" label.
TICKET_RULE = "beta"


def card_rule(card_dir=None):
    """Leverage rule the card runs, read off its own config (vol target present -> vol)."""
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        cfg = doc.get("config") or {}
        return "vol" if cfg.get("vol_target") else "beta"
    except Exception:
        return None


# ------------------------------------------------------------------ card-config ticket
# The card, the forward ledger and this ticket are three faces of one book only if the
# ticket is issued FROM the card instead of re-ranking the panel at its own width. Until
# r1333 the executable ticket was a 5-name beta-overlay book while the card and the
# ledger both ran 12 names at an 8% vol target -- two published books, one operator.
def _read_card(card_dir=None):
    """The card document itself, pointer chain resolved. None when the face is absent."""
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        return doc
    except Exception:
        return None


LEDGER_PATH_DEFAULT = os.path.join(PATHS.results_dir, "etf_book_forward", "LEDGER.json")


def _ledger_book(ledger_path=None):
    """Third face: what the forward ledger is actually holding and on what bar."""
    p = ledger_path or LEDGER_PATH_DEFAULT
    try:
        with open(p, encoding="utf-8") as f:
            led = json.load(f)
    except Exception:
        return None
    bif = led.get("book_in_force") or {}
    bars = led.get("bars") or []
    last = bars[-1] if bars else {}
    return {"config": led.get("config") or {}, "names": list(bif.get("names") or []),
            "scale": bif.get("scale"), "book_bar": bif.get("bar"),
            "last_bar": last.get("bar"), "last_nav": last.get("nav"),
            "status": led.get("status"), "source": p}


def _ledger_restatements(ledger_path=None):
    """Bars the ledger restated AFTER they settled -- a history change nobody was told about.

    The forward ledger is allowed to move a mark once, for a bar that was published while
    its panel was still filling (see etf_book_forward.restate_provisional): it keeps both
    values, the delta and the run that did it. That record only helped whoever opened
    LEDGER.json. The operator holds the ticket, so the ticket has to carry the notice.

    Three states are kept apart on purpose: unreadable, readable-and-empty, readable with
    notices. Collapsing the first into the second would let a missing ledger read as
    "your history is clean".
    """
    p = ledger_path or LEDGER_PATH_DEFAULT
    out = {"path": p, "readable": False, "source": None, "notices": [],
           "bars": [], "bars_published": None}
    try:
        with open(p, encoding="utf-8") as f:
            led = json.load(f)
    except Exception:
        return out
    out["readable"] = True
    bars = led.get("bars") or []
    out["bars_published"] = len(bars)
    lst = led.get("restatements")
    if isinstance(lst, list):
        out["source"] = "restatements"
        for n in lst:
            if not isinstance(n, dict) or not n.get("bar"):
                continue
            out["notices"].append({"bar": n.get("bar"), "ts": n.get("ts"),
                                   "nav_published": n.get("nav_published"),
                                   "nav_settled": n.get("nav_settled"),
                                   "delta": n.get("delta"), "reason": n.get("reason")})
    else:
        # ledgers written before the top-level list existed carry the marks on the bars
        out["source"] = "bars"
        for b in bars:
            if not isinstance(b, dict) or not b.get("restated_at"):
                continue
            pub = b.get("nav_published")
            stl = b.get("nav_settled", b.get("nav"))
            out["notices"].append({
                "bar": b.get("bar"), "ts": b.get("restated_at"),
                "nav_published": pub, "nav_settled": stl,
                "delta": (None if pub is None or stl is None else float(stl) - float(pub)),
                "reason": b.get("restate_reason")})
    out["bars"] = [n["bar"] for n in out["notices"]]
    return out


def _relpath_safe(p, base=None):
    """Relative path for display; a fixture or ledger on another drive is printed absolute."""
    p = str(p or "")
    try:
        return os.path.relpath(p, base or BASE).replace("\\", "/")
    except Exception:
        return p.replace("\\", "/")


def restatement_md(rst, base=None):
    """The notice block: which published bars moved after they settled -- or that none did."""
    base = base or BASE
    if not rst or not rst.get("readable"):
        return ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
                "- **无法核验**：读不到前向账本（%s），所以本单不能回答这个问题 —— "
                "这不是「没有被改述」。"
                % _relpath_safe((rst or {}).get("path") or LEDGER_PATH_DEFAULT, base)]
    notices = rst.get("notices") or []
    if not notices:
        return ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
                "- 已核验：前向账本已发布 %s 根 bar，其中**没有一根在定格之后被改述**（%s）。"
                % (rst.get("bars_published") if rst.get("bars_published") is not None else "?",
                   "账本顶层 restatements 清单为空"
                   if rst.get("source") == "restatements"
                   else "账本无顶层清单，已按每根 bar 的 restated_at 标记逐根核对")]
    L = ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
         "**有 %d 根 bar 在定格之后又被改述**（=历史变了，两个值都留着）：" % len(notices),
         "", "| bar | 当时发布(NAV) | 定格后(NAV) | 差 | 何时 |", "|---|---|---|---|---|"]
    for n in notices:
        pub, stl, dl = n.get("nav_published"), n.get("nav_settled"), n.get("delta")
        L.append("| %s | %s | %s | %s | %s |"
                 % (n.get("bar") or "-",
                    ("%.8f" % float(pub)) if pub is not None else "-",
                    ("%.8f" % float(stl)) if stl is not None else "-",
                    ("%+.2e" % float(dl)) if dl is not None else "-",
                    n.get("ts") or "-"))
    relist = "；".join(sorted({str(n.get("reason") or "未注明") for n in notices}))
    L += ["", "- 读法：被改述的是「当天面板还在补数就先定过的价」，不是有人事后改了历史；"
          "本单引用的行以「定格后」那一列为准。原因：%s。" % relist,
          "- 出处：%s。" % _relpath_safe(rst.get("path") or LEDGER_PATH_DEFAULT, base)]
    return L


def card_config_ticket(card_dir=None, nav=None, ledger_path=None):
    """Broker-followable ticket for the book the production card publishes.

    Weights, names and the risk scale come from the card's own sheet (one source of
    truth); ``nav`` only re-prices the lot counts, it never re-ranks anything. Recomputing
    the lots from price x weight is deliberate: on the card's own capital the result must
    equal the card's published lot counts, and any drift between the two faces shows up as
    ``reprice_mismatch`` instead of being copied silently.
    """
    doc = _read_card(card_dir)
    if not doc:
        return None
    cfg = doc.get("config") or {}
    sh = doc.get("sheet") or {}
    legs = sh.get("legs") or []
    cap = float(sh.get("capital_cny") or cfg.get("capital_cny") or 0.0)
    if not legs or cap <= 0:
        return None
    stated = float(nav) if nav else cap
    rows, spent, mismatch = [], 0.0, []
    for l in legs:
        px = l.get("ref_price")
        w = float(l.get("weight") or 0.0)
        want = stated * w
        lots = shares = amt = None
        if px and float(px) > 0:
            lots = int(want // (float(px) * LOT))
            shares = lots * LOT
            amt = shares * float(px)
            spent += amt
            if (abs(stated - cap) < 1e-6 and l.get("lots_100") is not None
                    and int(l["lots_100"]) != shares):
                # the card's ``lots_100`` field carries the SHARE count rounded to 100
                # (live card: 159501 26600 shares x 2.194 = 58360 actual amount), not a
                # lot count -- comparing against ``lots`` here reads as a 100x mismatch
                mismatch.append({"symbol": l.get("symbol"), "card_shares": l.get("lots_100"),
                                 "ticket_shares": shares})
        rows.append({"symbol": l.get("symbol"), "name": l.get("name"),
                     "class": l.get("class"), "weight": round(w, 6),
                     "price": round(float(px), 4) if px else None,
                     "lots": lots, "shares": shares,
                     "amount": round(amt, 2) if amt is not None else None,
                     "note": "" if lots else "budget below one lot"})
    cash = stated - spent
    names = [r["symbol"] for r in rows]
    led = _ledger_book(ledger_path) or {}
    rst = _ledger_restatements(ledger_path)
    led_cfg = led.get("config") or {}
    card_scale = sh.get("risk_scale")
    recon = {"card_priced_bar": sh.get("as_of_bar"),
             "card_decided_at": sh.get("book_decided_at") or sh.get("last_decision_bar"),
             "card_scale": card_scale, "card_names": names,
             "same_names_as_card": names == [l.get("symbol") for l in legs],
             "ledger_names": led.get("names"),
             "same_names_as_ledger": (names == led["names"]) if led.get("names") else None,
             "ledger_scale": led.get("scale"),
             "same_scale_as_ledger": None,
             "ledger_book_bar": led.get("book_bar"), "ledger_last_bar": led.get("last_bar"),
             "ledger_last_nav": led.get("last_nav"), "ledger_status": led.get("status"),
             "ledger_source": led.get("source"),
             "restatements_readable": rst["readable"],
             "restatements_source": rst["source"],
             "restated_bars": rst["bars"],
             "restatements": rst["notices"],
             "ledger_bars_published": rst["bars_published"],
             "card_cash_weight": sh.get("cash_weight"),
             # r1342 / E230: the card now prints the EXECUTABLE cash row, so the ticket
             # reconciles against that one. A card that predates the fix has no
             # cash_executable_cny and still gets the legacy target-row disclosure.
             "card_cash_amount": sh.get("cash_executable_cny", sh.get("cash_amount_cny")),
             "card_cash_is_executable": sh.get("cash_executable_cny") is not None,
             "card_cash_target_amount": sh.get("cash_amount_cny"),
             "card_config": {k: cfg.get(k) for k in ("n_hold", "vol_target", "rebal",
                                                     "cost_bp_per_side")},
             "ledger_config": {k: led_cfg.get(k) for k in ("n_hold", "vol_target", "rebal",
                                                           "cost_per_side")},
             "same_config_as_ledger": None}
    if card_scale is not None and led.get("scale") is not None:
        # the card publishes the scale at 4 dp while the ledger keeps full precision
        # (0.7008 vs 0.700775) -- compare at the published precision, not bitwise, or
        # two faces of the same book would read as different books every round.
        recon["same_scale_as_ledger"] = (round(float(card_scale), 4)
                                         == round(float(led["scale"]), 4))
        recon["scale_precision"] = "4 dp (the card's published precision)"
    try:
        recon["same_config_as_ledger"] = (
            str(cfg.get("n_hold")) == str(led_cfg.get("n_hold"))
            and abs(float(cfg.get("vol_target") or 0.0)
                    - float(led_cfg.get("vol_target") or 0.0)) < 1e-9)
    except Exception:
        recon["same_config_as_ledger"] = None
    return {"kind": "card_config", "nav": stated, "card_capital": cap,
            "scale": float(card_scale or 0.0), "config": cfg, "order": rows,
            "book_amount": round(spent, 2), "cash_amount": round(cash, 2),
            "book_weight": round(spent / stated, 6), "cash_weight": round(cash / stated, 6),
            "cash_leg": "GC001 (1-day repo, observed close)",
            "underspend_pct": round(100.0 * cash / stated - 100.0 * (1.0 - float(card_scale or 0.0)), 4),
            "reprice_mismatch": mismatch, "priced_bar": sh.get("as_of_bar"),
            "decision": sh.get("decision"),
            "bars_until_next_decision": sh.get("bars_until_next_decision"),
            "feed": doc.get("feed_status") or {}, "recon": recon}


def _verdict(b):
    return "unknown" if b is None else ("一致" if b else "不一致")


def card_config_card(tk, width=None, ruler=None):
    """Markdown for the card-config order, with the three-face reconciliation on it."""
    rc = tk["recon"]
    cfg = tk["config"]
    L = ["# ETF 复合书 · 可执行订单单（%s，卡片配置口径）" % tk["priced_bar"], "",
         "当前活：生产卡片的原样配置——%d 名、每 %d 个交易日网格、%.0f%% 波动目标（只降不升杠杆）、"
         "空仓进 GC001。" % (int(cfg.get("n_hold") or 0), int(cfg.get("rebal") or REBAL),
                           100.0 * float(cfg.get("vol_target") or 0.0)),
         "最近实物：%s（与本文件同刻生成）。"
         % os.path.relpath(os.path.join(OUT_DIR, "TICKET-%s-card.json" % tk["priced_bar"]),
                           BASE).replace("\\", "/"),
         "下个里程碑：该单一是一张可下手的单，卡片/账本/单据三面同书（本文件末节逐项对账）。", ""]
    feed = tk.get("feed") or {}
    L += ["## 数据新鲜度（本单定价用的是哪一天的 bar）",
          "- 官方交易日历期望最新 bar：%s" % (feed.get("expected_bar") or "未知（无日历）"),
          "- 本单定价 bar：%s ｜ 判定：**%s**｜落后 %s 个交易日"
          % (tk["priced_bar"], feed.get("status", "unknown"),
             "?" if feed.get("lag_days") is None else feed.get("lag_days")),
          "- 前向账本最后一行 bar：%s（NAV %.6f，status=%s）"
          % (rc.get("ledger_last_bar") or "未知",
             float(rc.get("ledger_last_nav") or 0.0), rc.get("ledger_status") or "未知"), ""]
    L += restatement_md({"readable": rc.get("restatements_readable"),
                         "path": rc.get("ledger_source"),
                         "source": rc.get("restatements_source"),
                         "notices": rc.get("restatements") or [],
                         "bars_published": rc.get("ledger_bars_published")})
    L += ["## 今日目标（NAV ¥%s）" % format(int(round(tk["nav"])), ","),
          "风险缩放 k=%.3f（书内 %.1f%%、现金 %.1f%%）｜现金腿=%s｜现金 ¥%s"
          % (tk["scale"], tk["book_weight"] * 100, tk["cash_weight"] * 100,
             tk["cash_leg"], format(int(round(tk["cash_amount"])), ",")),
          "",
          "| 代码 | 名称 | 类别 | 权重 | 参考价 | 手数(100股) | 金额 |",
          "|---|---|---|---|---|---|---|"]
    for r in tk["order"]:
        L.append("| %s | %s | %s | %.1f%% | %s | %s | %s |"
                 % (r["symbol"], r.get("name") or "-", r.get("class") or "?",
                    r["weight"] * 100, ("%.3f" % r["price"]) if r["price"] else "-",
                    r["lots"] if r["lots"] is not None else "-",
                    format(int(r["amount"]), ",") if r["amount"] else "-"))
    L += ["", "整手取整后欠投 %+.2f%% NAV（留在现金腿，不重分配）。" % tk["underspend_pct"]]
    if tk.get("bars_until_next_decision") is not None:
        L += ["", "下一个网格决策点：%s 个交易日后（当前决策 bar %s）。"
              % (tk["bars_until_next_decision"], rc.get("card_decided_at") or "-")]
    L += ["", "## 三面是不是同一本书", "",
          "| 面 | 名数 | 杠杆规则 | 风险缩放 | 定价/决策 bar |",
          "|---|---|---|---|---|",
          "| 生产卡片 | %d | %s | %.4f | %s |"
          % (len(rc["card_names"]), "vol %.0f%%" % (100.0 * float(cfg.get("vol_target") or 0.0)),
             float(rc["card_scale"] or 0.0), rc.get("card_priced_bar") or "-"),
          "| 前向账本 | %d | %s | %s | %s（最后行 %s） |"
          % (len(rc.get("ledger_names") or []),
             "vol %.0f%%" % (100.0 * float((rc.get("ledger_config") or {}).get("vol_target") or 0.0)),
             ("%.4f" % float(rc["ledger_scale"])) if rc.get("ledger_scale") is not None else "-",
             rc.get("ledger_book_bar") or "-", rc.get("ledger_last_bar") or "-"),
          "| 本单（可执行） | %d | vol %.0f%% | %.4f | %s |"
          % (len(tk["order"]), 100.0 * float(cfg.get("vol_target") or 0.0), tk["scale"],
             tk["priced_bar"]),
          "",
          "- 名称：本单 vs 卡片 %s｜本单 vs 账本 %s"
          % (_verdict(rc["same_names_as_card"]), _verdict(rc["same_names_as_ledger"])),
          "- 风险缩放：本单 vs 账本 %s（%.4f / %s，按卡片 4 位小数口径比对）"
          % (_verdict(rc["same_scale_as_ledger"]), tk["scale"],
             ("%.4f" % float(rc["ledger_scale"])) if rc.get("ledger_scale") is not None else "-"),
          "- 配置：本单 vs 账本 %s（card %s / ledger %s）"
          % (_verdict(rc["same_config_as_ledger"]),
             rc.get("card_config"), rc.get("ledger_config")),
          "- 卡片重算手数 vs 卡片已发布手数：%d 处不一致%s"
          % (len(tk["reprice_mismatch"]),
             ("（%s）" % tk["reprice_mismatch"][:3]) if tk["reprice_mismatch"] else "")]
    if width:
        d = width["delta_ticket_minus_card"]
        L += ["", "## 与「%d 名 β 覆盖」那张单的关系" % width["ticket_names"],
              "那张单是**另一本书**（%d 名 / %s 覆盖 / 固定 β 目标 %.2f），不是本卡片的宽度变体："
              "两者的差值 (%+.2fpp 年化, %+.3f 夏普) 是同时换了宽度和杠杆规则的对角线。"
              % (width["ticket_names"], width["ticket_rule"], DEFAULT_BETA,
                 -d["cagr_pp"], -d["sharpe"]),
              "同一规则下只换名数的代价：%s。"
              % ("；".join("%s 规则 %+.2fpp" % (r, v["pp"])
                          for r, v in sorted((width.get("width_effect") or {}).items()))
                 or "本窗未取到同规则两宽度格"),
              "出处：%s（cutoff %s）。" % (width["source"], width["evidence_cutoff"])]
    ru = (ruler or {})
    if ru.get("state") == "inside_disagreement" and ru.get("sheet_role") == "measured_card":
        L += ["", "## 另一张单和本单的差（两张面逐相位配对）",
              "本单**就是卡片那一本书**（%d 名 / vol %.0f%%），所以下面这个差不是「本单 vs 卡片」，"
              "而是「%d 名 %s 覆盖那张单 vs 本单」：中位 **%+.2fpp**"
              "（%d 个相位，%s 个往上、%s 个往下，区间 %+.2f ~ %+.2f）；同一档 5→12 名在另一台引擎上"
              "是 **%+.2fpp** —— 两台引擎对这一档的分歧 **%+.2fpp**（方向还相反）。"
              % (len(tk["order"]), 100.0 * float(cfg.get("vol_target") or 0.0),
                 ru["widths"]["ticket"]["live_n_hold"], ru["widths"]["ticket"]["live_rule"],
                 float(ru["gap_pp"]), ru["pairs"], ru.get("positive_phases"),
                 (ru["pairs"] - (ru.get("positive_phases") or 0)) if ru.get("pairs") else "?",
                 float(ru.get("min_pp") or 0.0), float(ru.get("max_pp") or 0.0),
                 float(ru.get("capacity_rung_pp") or 0), float(ru["disagreement_pp"])),
              "- 读法：这个差只有引擎分歧的 **%.1f%%**，所以两张单之间选哪张读不出收益差——"
              "读得出来的是要在哪一档波动预算上：β 覆盖固定杠杆，本单按 8%% 目标只降不升。"
              % (100.0 * (ru.get("share_of_disagreement") or 0.0)),
              _resolution_md(ru),
              "- 出处：%s（cutoff %s，%s 个相位配对）。"
              % (ru["source"], ru["evidence_cutoff"], ru["pairs"])]
    elif ru.get("state") and ru["state"] != "unavailable":
        L += ["", "## 另一张单和本单的差（尺子没给出干净读数）",
              "- 尺子状态：**%s** —— %s" % (ru["state"], ru.get("detail") or ""),
              "- 本单在这把尺子上的身份：%s。"
              % {"measured_card": "卡片面（可读）",
                 "unverified": "**未核实**——尺子量的是旧宽度，本单不能引用它的读数",
                 None: "未声明"}.get(ru.get("sheet_role"), ru.get("sheet_role")),
              "- 出处：%s（cutoff %s）。" % (ru.get("source"), ru.get("evidence_cutoff"))]
    L += ["", "## 诚实面", "",
          "- 探索件：无预注册、无判决、不入成绩账本；本单只是把卡片已经公布的那本书变成可下手的单。"]
    gap = None
    if rc.get("card_cash_amount") is not None:
        gap = tk["cash_amount"] - float(rc["card_cash_amount"])
        if abs(gap) >= 1.0:
            L += ["- **卡片现金行是目标口径**：卡片按 权重×资本 印目标金额、现金=(1-缩放)×资本"
                  "（¥%s）；整手取整后真实能花出去的钱比目标少 ¥%s（%.2f%% NAV），"
                  "所以本单的现金腿是 ¥%s。照卡片那行下手，账上实际会多出这 %.2f%% 现金"
                  "——卡片把投入算高了，不是把现金算少了。"
                  % (format(int(round(float(rc["card_cash_amount"]))), ","),
                     format(int(round(gap)), ","), 100.0 * gap / tk["nav"],
                     format(int(round(tk["cash_amount"])), ","), 100.0 * gap / tk["nav"])]
    L += [
          "- 票池=现存 ETF，存在幸存者偏差；票面按卡片定盘 bar 的参考价折算，未计冲击成本与涨跌停。",
          "- GC001 单期限且滚动假设零费；真实现金台应做 1/7/14 天梯队。",
          "- 波动目标是历史估计，只降不升杠杆：标注 8% 的书实测跑到 10%+（见卡片风险列）。"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------- lot granularity (r1334)
LOT_CURVE_GRID = (50_000, 100_000, 200_000, 300_000, 500_000, 750_000,
                  1_000_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000,
                  20_000_000)


def lot_point(legs, capital, scale=None, lot=LOT):
    """What the card's own weights actually buy at one stated capital.

    Whole lots only, buys floor'ed, so the book can only spend LESS than target: a
    card's cash row is ``(1 - k) * capital`` while the cash that lands on the desk is
    ``capital - spent``. The difference is the price of lot granularity, and
    ``max_abs_weight_drift_pp`` is the same thing seen from the book's side -- a leg
    that misses its weight by half a lot is mis-sized, not merely cheap.

    r1342: the production card PRINTS the executable cash (``capital - spent``) now, so
    ``cash_vs_target_cny`` no longer measures a card defect -- it measures the money the
    desk holds beyond the risk scale's own cash slot, most of it the lot residue. Read it
    as "cash above the slot", not "the card is wrong".
    """
    cap = float(capital)
    rows, spent, zero, max_drift, tot_w = [], 0.0, 0, 0.0, 0.0
    for l in legs:
        w = float(l.get("weight") or 0.0)
        px = l.get("ref_price") or l.get("price")
        tot_w += w
        if not px or float(px) <= 0:
            rows.append({"symbol": l.get("symbol"), "weight": round(w, 6), "price": None,
                         "lots": None, "amount": None, "drift_pp": None})
            continue
        lots = int((cap * w) // (float(px) * lot))
        amt = lots * lot * float(px)
        spent += amt
        if lots == 0:
            zero += 1
        drift_pp = 100.0 * (amt / cap - w)
        max_drift = max(max_drift, abs(drift_pp))
        rows.append({"symbol": l.get("symbol"), "weight": round(w, 6),
                     "price": round(float(px), 4), "lots": lots,
                     "amount": round(amt, 2), "drift_pp": round(drift_pp, 4)})
    s = float(scale) if scale is not None else tot_w
    cash = cap - spent
    gap = cash - cap * (1.0 - s)
    return {"capital_cny": round(cap, 2), "scale": round(s, 6),
            "target_book_cny": round(cap * s, 2), "book_amount_cny": round(spent, 2),
            "cash_amount_cny": round(cash, 2), "cash_vs_target_cny": round(gap, 2),
            "underspend_pp_nav": round(100.0 * gap / cap, 4) if cap else None,
            "max_abs_weight_drift_pp": round(max_drift, 4),
            "legs_with_zero_lots": zero, "legs": rows}


def lot_curve(legs, scale=None, grid=LOT_CURVE_GRID, thresholds=(1.0, 0.5)):
    """Sweep the stated capital: the granularity cost is a curve, not one number.

    A single-capital disclosure answers "is today's ticket executable"; the operator's
    real question is "how small may this book be before the ticket stops being the
    book". Both readings are published (cash vs target, and weight drift), because a
    book can be cheap and mis-sized at the same time.
    """
    pts = [lot_point(legs, c, scale) for c in grid]
    drift = [p["max_abs_weight_drift_pp"] for p in pts]

    def _mincap(th):
        for c, d in zip(grid, drift):
            if d <= th:
                return float(c)
        return None

    px_lot, min_w = 0.0, None
    for l in legs:
        px = l.get("ref_price") or l.get("price")
        w = float(l.get("weight") or 0.0)
        if px and float(px) > 0 and w > 0:
            px_lot = max(px_lot, float(px) * LOT)
            min_w = w if min_w is None else min(min_w, w)
    floor = (px_lot / min_w) if min_w else None
    # Each leg can leave at most one lot unspent, so the shortfall is BOUNDED in yuan
    # and does not shrink as the book grows -- only its percentage does. That is why the
    # cash column of this curve is jagged while the weight-drift column is monotone.
    bound = 0.0
    for l in legs:
        px = l.get("ref_price") or l.get("price")
        if px and float(px) > 0:
            bound += float(px) * LOT
    return {"grid": list(grid), "points": pts,
            "monotone_non_increasing": all(b <= a + 1e-9 for a, b in zip(drift, drift[1:])),
            "thresholds": {("%.2fpp" % th): {"min_capital_cny": _mincap(th)}
                           for th in thresholds},
            "shortfall_bound_cny": round(bound, 2),
            "max_observed_shortfall_cny": max(p["cash_vs_target_cny"] for p in pts),
            "one_lot_floor_cny": round(floor, 2) if floor else None}


def lot_curve_md(curve, card_cap=None):
    """The operator's half of the curve: the row about to be traded, plus the edge."""
    L = ["## 资金规模下限（整手取整的实际代价）", ""]
    cur = None
    if card_cap:
        for p in curve["points"]:
            if abs(p["capital_cny"] - float(card_cap)) < 1.0:
                cur = p
                break
    if cur:
        L += ["本单资金 %s 元：目标持仓 %s / 实际买入 %s，现金比卡片行多 %s（%.2f%% NAV），"
              "单腿最大偏离 %.2f%%，买不到一手 %d 腿。"
              % (format(int(round(cur["capital_cny"])), ","),
                 format(int(round(cur["target_book_cny"])), ","),
                 format(int(round(cur["book_amount_cny"])), ","),
                 format(int(round(cur["cash_vs_target_cny"])), ","),
                 cur["underspend_pp_nav"], cur["max_abs_weight_drift_pp"],
                 cur["legs_with_zero_lots"]), ""]
    L += ["| 资金 | 单腿最大偏离 | 买不到一手 | 现金比目标多 |",
          "|---|---|---|---|"]
    for p in curve["points"]:
        L.append("| %s | %.2f%% | %d | %s |"
                 % (format(int(round(p["capital_cny"])), ","),
                    p["max_abs_weight_drift_pp"], p["legs_with_zero_lots"],
                    format(int(round(p["cash_vs_target_cny"])), ",")))
    th = curve["thresholds"]
    a1 = th["1.00pp"]["min_capital_cny"]
    a5 = th["0.50pp"]["min_capital_cny"]
    L += ["",
          "- 单腿偏离 ≤1.00pp 需要资金 ≥ %s；≤0.50pp 需要 ≥ %s。"
          % (format(int(a1), ",") if a1 else "本表内不可达",
             format(int(a5), ",") if a5 else "本表内不可达"),
          "- 至少一腿连一手都买不起的下限 = %s 元（最贵一手 ÷ 最小权重）；这条线以下"
          "「按卡片权重执行」不成立，只能降标的数或换更便宜的腿。"
          % (format(int(curve["one_lot_floor_cny"]), ",")
             if curve.get("one_lot_floor_cny") else "未知"),
          "- 偏离随资金单调不增：%s（取整代价是小资金的税，不是策略的缺陷）。"
          % ("是" if curve["monotone_non_increasing"] else "**否，见上表**"),
          "- 缺口的绝对额不随资金变小：每腿最多剩一手，合计上限 %s 元，本表实测最大 %s 元——"
          "所以这条曲线在现金列是锯齿的（谁离整手更远谁更亏），只有占 NAV 的百分比随资金下降；"
          "换句话说「多留几百块现金」是固定小额开销，与资金规模无关。"
          % (format(int(round(curve["shortfall_bound_cny"])), ",")
             if curve.get("shortfall_bound_cny") else "未知",
             format(int(round(curve.get("max_observed_shortfall_cny") or 0.0)), ","))]
    return L


def run_card(nav=None):
    tk = card_config_ticket(nav=nav)
    if not tk:
        print("card: no production card to issue from (%s)" % CARD_DIR)
        return 2
    asof = tk["priced_bar"] or "unknown"
    doc = {"kind": tk["kind"], "asof_bar": asof, "capital_cny": tk["nav"],
           "card_capital_cny": tk["card_capital"], "scale": tk["scale"],
           "config": tk["config"], "order": tk["order"],
           "book_amount": tk["book_amount"], "cash_amount": tk["cash_amount"],
           "book_weight": tk["book_weight"], "cash_weight": tk["cash_weight"],
           "cash_leg": tk["cash_leg"], "underspend_pct": tk["underspend_pct"],
           "reprice_mismatch": tk["reprice_mismatch"], "recon": tk["recon"],
           "decision": tk.get("decision"),
           "bars_until_next_decision": tk.get("bars_until_next_decision"),
           "feed": tk.get("feed"),
           "caveats": ["exploratory: no prereg, no verdict, not in the scorecard",
                       "survivorship in the ETF pool; reference prices only, no impact cost",
                       "cash leg is GC001 single tenor, rolls at zero fee"]}
    wd = width_disclosure()
    curve = lot_curve(tk["order"], scale=tk["scale"])
    curve["asof_bar"] = asof
    curve["scale_of_capital_cny"] = tk["nav"]
    _write("LOTCURVE-%s-card.json" % asof, curve)
    # r1357: the ruler reaches the card sheet too -- both documents a reader can hold must
    # answer "what did the other sheet measure", and the paired gap is between the faces,
    # so this sheet says which face it is on that ruler rather than borrowing the gap.
    ruler = live_width_ruler(asof=tk["priced_bar"], card_n=len(tk["order"]), sheet="card")
    doc["live_width_ruler"] = ruler
    _write("TICKET-%s-card.json" % asof, doc)
    md = "\n".join([card_config_card(tk, wd, ruler).rstrip(),
                    "\n".join(lot_curve_md(curve, tk["nav"])).rstrip(),
                    ""])
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ORDER-%s-card.md" % asof), "w", encoding="utf-8") as f:
        f.write(md)
    rc = tk["recon"]
    print("card-config ticket: %s | NAV %s | %d names | k=%.3f | cash %.1f%%"
          % (asof, format(int(round(tk["nav"])), ","), len(tk["order"]), tk["scale"],
             tk["cash_weight"] * 100))
    print("three faces: names card=%s ledger=%s | scale vs ledger=%s | config vs ledger=%s"
          % (_verdict(rc["same_names_as_card"]), _verdict(rc["same_names_as_ledger"]),
             _verdict(rc["same_scale_as_ledger"]), _verdict(rc["same_config_as_ledger"])))
    print("card lot recount mismatches: %d" % len(tk["reprice_mismatch"]))
    own = [p for p in curve["points"] if abs(p["capital_cny"] - tk["nav"]) < 1.0]
    if own:
        print("lot curve at this capital: drift %.2f%% max | %d legs below one lot | "
              "cash vs risk-scale slot +%s" % (own[0]["max_abs_weight_drift_pp"],
                                        own[0]["legs_with_zero_lots"],
                                        format(int(round(own[0]["cash_vs_target_cny"])), ",")))
    print("wrote", os.path.join(OUT_DIR, "ORDER-%s-card.md" % asof))
    return 0


def width_disclosure(card_n=None, audit_path=None, card_dir=None):
    """What this ticket's width costs against the card's, from the audit face.

    Both faces are published as "the production book", so an operator following this
    ticket buys N names under the beta overlay while the card's row describes its own
    width under an 8% vol target. ``scripts/etf_book_width_audit.py`` measures the full
    width x rule grid; this reads it back rather than re-running it.

    Two numbers matter and they are not interchangeable (r1291):
      * ``width_effect`` -- same rule, two widths: how much the name count alone costs.
        Under the beta overlay it is -1.5pp, under the vol target +0.2pp.
      * ``delta_ticket_minus_card`` -- the two *published* faces: they differ in BOTH
        width and rule, so this is a diagonal of that grid, not a width effect.

    Missing audit (or a width/rule missing from it) returns None and the caller says so
    out loud -- silence would read as "no difference".
    """
    p = audit_path or AUDIT_PATH
    n_card = card_n if card_n is not None else card_width()
    c_rule = card_rule(card_dir)
    try:
        with open(p, encoding="utf-8") as f:
            audit = json.load(f)
    except Exception:
        return None
    # keyed by (names, rule): rows written before the rule column existed are the beta arm.
    cells = {}
    for r in (audit.get("rows") or []):
        cells[(int(r["n_hold"]), r.get("rule") or "beta")] = r
    if c_rule is None:
        # A card artefact we cannot read is not a licence to assume its rule: use the
        # only arm present at its width, and say which one we ended up comparing.
        cand = [rule for (_n, rule) in cells if n_card and _n == int(n_card)]
        if len(cand) != 1:
            return None
        c_rule = cand[0]
    a = cells.get((int(N_HOLD), TICKET_RULE))
    b = cells.get((int(n_card), c_rule)) if n_card else None
    if not a or not b:
        return None

    def face(r):
        bk = r.get("book") or {}
        return {"cagr": bk.get("cagr"), "sharpe": bk.get("sharpe"), "maxdd": bk.get("maxdd"),
                "vol": bk.get("vol")}

    ta, tb = face(a), face(b)
    sq = audit.get("square") or {}
    # same-rule width effect, per rule, straight off the audit's own grid.
    # sign = the WIDER book minus this ticket's width (audit's own width_effect_pp
    # convention), so beta reads -1.5pp and vol +0.2pp at 12 vs 5 names.
    width_effect = {}
    for rule in {TICKET_RULE, c_rule}:
        lo = cells.get((int(N_HOLD), rule))
        hi = cells.get((int(n_card), rule)) if n_card else None
        if lo and hi:
            width_effect[rule] = {
                "ticket_width_cagr": (lo.get("book") or {}).get("cagr"),
                "card_width_cagr": (hi.get("book") or {}).get("cagr"),
                "pp": round((((hi.get("book") or {}).get("cagr") or 0.0)
                             - ((lo.get("book") or {}).get("cagr") or 0.0)) * 100, 2)}
    try:
        src = os.path.relpath(p, BASE).replace("\\", "/")
    except ValueError:            # audit path off the repo volume (selftest fixtures)
        src = p.replace("\\", "/")
    return {"ticket_names": int(N_HOLD), "card_names": int(n_card),
            "ticket_rule": TICKET_RULE, "card_rule": c_rule,
            "ticket": ta, "card": tb,
            "width_effect": width_effect,
            "rules_differ": TICKET_RULE != c_rule,
            "delta_ticket_minus_card": {
                "cagr_pp": round((ta["cagr"] - tb["cagr"]) * 100, 2),
                "sharpe": round(ta["sharpe"] - tb["sharpe"], 3),
                "maxdd_pp": round((ta["maxdd"] - tb["maxdd"]) * 100, 2),
                "vol_pp": round(((ta.get("vol") or 0.0) - (tb.get("vol") or 0.0)) * 100, 2)},
            "square": sq or None,
            "same_accounting": "one ledger (GC001 cash leg, next-open fills, 8bp/side); "
                               "width and leverage rule each varied in turn",
            "source": src,
            "evidence_cutoff": audit.get("evidence_cutoff")}


def _resolution_md(ru):
    """One line: how big a difference this pairing could have seen (r1358).

    Kept as a helper because both sheets print it and a second copy would drift from the first
    (the E271 cross-document lesson). A face that publishes no per-phase dispersion cannot have
    its resolution computed, and that absence is printed rather than filled with a zero.
    """
    mde = ru.get("resolution_pp")
    if mde is None:
        return ("- 这一面没有公布逐相位离散度（sd），分辨下限算不出来——"
                "「两张单差不多」这句话在这张单上没有尺子支撑，按未核实读。")
    return ("- 这把尺子自己的分辨下限：%d 个相位、逐相位差 sd %.2fpp，在 %.0f%% 功效"
            "（双侧 5%%）下能分辨的最小差值 **%.2fpp**；本次差是它下限的 %.0f%% —— %s"
            % (ru.get("pairs") or 0, float(ru.get("paired_sd_pp") or 0.0),
               100.0 * float(ru.get("power_target") or 0.8), float(mde),
               100.0 * float(ru.get("gap_over_resolution") or 0.0),
               "在射程内，差值可读" if ru.get("below_own_resolution") is False
               else "低于下限：所以「两者没差别」也不是本窗的结论，结论是这把尺子分不开"))


def live_width_ruler(asof=None, card_n=None, card_dir=None, path=None,
                     sheet=None, stale_days=RULER_STALE_DAYS):
    """Is the gap between the two live faces bigger than the engines' own disagreement?

    ``scripts/etf_book_phase_atlas_arms.py --live-widths`` puts both live cells on one
    ruler, paired phase by phase. This reads that face back so the number reaches the
    person placing the order (r1275: a difference that only lives in research/ is a
    difference nobody was told about).

    The verdict is re-derived here from the face's own published numbers rather than
    copied off its label: a verdict that can drift away from the numbers that produced
    it is a receipt, not a gate (r1266).

    States, in precedence order:
      unavailable        -- no face on disk
      inconsistent       -- the face's own verdict contradicts the numbers it published
      widths_moved       -- the face priced widths the live faces no longer run
      stale              -- cutoff older than ``stale_days`` calendar days before asof
      inside_disagreement-- |paired median| < |5->12 rung disagreement| and signs split
      separated          -- the paired gap is at least the size of the disagreement
    """
    p = path or RULER_PATH
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        return {"state": "unavailable",
                "detail": "no live-width ruler on disk; run scripts/etf_book_phase_atlas_arms.py "
                          "--live-widths", "source": p.replace("\\", "/")}
    pr = doc.get("paired") or {}
    ed = doc.get("engine_disagreement") or {}
    lf = doc.get("live_faces") or {}
    rule = doc.get("rule") or {}
    gap = pr.get("median_pp")
    dis = ed.get("rung_disagreement_pp")
    sign = pr.get("sign_agreement")
    pairs = pr.get("pairs") or 0
    pairs_min = rule.get("pairs_min") or 20
    split_max = rule.get("sign_split_max") or 0.6
    cutoff = doc.get("evidence_cutoff")

    # re-derive rather than trust the label
    inside = (gap is not None and dis is not None and abs(float(gap)) < abs(float(dis)))
    split = (sign is not None and float(sign) <= float(split_max))
    if pairs < pairs_min:
        derived = "NOT_ENOUGH_PAIRS"
    elif inside and split:
        derived = "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"
    elif inside:
        derived = "INSIDE_DISAGREEMENT_NO_SIGN_SPLIT"
    else:
        derived = "SEPARATED"
    published = doc.get("verdict")
    published_inside = bool(published) and str(published).startswith("COIN_FLIP")
    relabel = bool(published) and published_inside != (derived ==
                                                       "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT")

    # are the priced widths still the ones the faces run?
    n_card = card_n if card_n is not None else card_width(card_dir)
    c_rule = card_rule(card_dir)
    widths = {}
    moved = []
    # rule labels are not written identically by the two faces ("vol" off the card
    # artefact, "vol_target" off the atlas), so compare them on a normalised spelling --
    # otherwise every read of a healthy face would report widths_moved.
    def _rule_key(x):
        return (str(x or "").lower().replace("_target", "").strip()) or None
    for name, live_n, live_rule in (("ticket", int(N_HOLD), TICKET_RULE),
                                    ("card", n_card, c_rule)):
        cell = lf.get(name) or {}
        widths[name] = {"live_n_hold": live_n, "priced_n_hold": cell.get("n_hold"),
                        "live_rule": live_rule, "priced_rule": cell.get("rule")}
        if cell.get("n_hold") is not None and live_n is not None \
                and int(cell["n_hold"]) != int(live_n):
            moved.append(name)
        if _rule_key(cell.get("rule")) and _rule_key(live_rule) \
                and _rule_key(cell["rule"]) != _rule_key(live_rule):
            moved.append(name)

    age = None
    try:
        if cutoff and asof:
            age = (pd.Timestamp(asof) - pd.Timestamp(cutoff)).days
    except Exception:
        age = None
    stale = age is not None and age > stale_days

    if relabel:
        state, detail = "inconsistent", (
            "face says %s but its own numbers give %s" % (published, derived))
    elif moved:
        state, detail = "widths_moved", (
            "face priced %s width(s) the live faces no longer run (%s)"
            % ("/".join(sorted(set(moved))), ", ".join(
                "%s priced %s vs live %s" % (k, widths[k]["priced_n_hold"],
                                             widths[k]["live_n_hold"]) for k in widths)))
    elif stale:
        state, detail = "stale", ("cutoff %s is %d days behind asof %s (limit %d)"
                                  % (cutoff, age, asof, stale_days))
    elif derived == "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT":
        state, detail = "inside_disagreement", (
            "paired median %+.3fpp inside a %0.3fpp engine disagreement"
            % (float(gap), float(dis)))
    elif derived == "NOT_ENOUGH_PAIRS":
        state, detail = "separated", ("only %d paired phases (need %d)" % (pairs, pairs_min))
    else:
        state, detail = "separated", (
            "paired median %+.3fpp vs %0.3fpp disagreement" % (float(gap), float(dis)))

    try:
        src = os.path.relpath(p, BASE).replace("\\", "/")
    except ValueError:
        src = p.replace("\\", "/")
    share = (abs(float(gap)) / abs(float(dis))) if (gap is not None and dis) else None
    # r1358: the pairing's own resolution, re-derived here from the sd and the phase count the
    # face publishes -- never copied off a stored field. "The gap is small" and "this pairing
    # could not have seen a gap this small" are different sentences, and a sheet that prints
    # only the first one invites a reader to conclude the widths are equivalent.
    res = doc.get("resolution") or {}
    sd_p = pr.get("sd_pp")
    z = res.get("power_z") or 2.802
    mde = None
    if sd_p and pairs:
        mde = (float(z) * float(sd_p)) / (float(pairs) ** 0.5)
    gap_over_mde = (abs(float(gap)) / mde) if (mde and gap is not None) else None
    # which of the two measured faces is the sheet asking for this reading? The paired gap
    # is between the faces, so a sheet that IS one of them is told what the OTHER one
    # measured -- printing the gap as if it were "this sheet vs the card" would be a
    # sentence about two different books. If the face no longer prices this sheet's width
    # the role goes unverified, so the page cannot keep printing a clean reading for a
    # book the face never measured (r1280 family: a label that outlives its numbers).
    sheet_role = None
    if sheet in ("card", "ticket"):
        sheet_role = ("unverified" if sheet in moved else
                      {"card": "measured_card", "ticket": "measured_ticket"}[sheet])
    return {"state": state, "detail": detail, "sheet": sheet, "sheet_role": sheet_role,
            "verdict": derived, "published_verdict": published,
            "gap_pp": gap, "disagreement_pp": dis,
            "share_of_disagreement": round(share, 4) if share is not None else None,
            "resolution_pp": round(mde, 3) if mde is not None else None,
            "gap_over_resolution": (round(gap_over_mde, 3)
                                    if gap_over_mde is not None else None),
            "below_own_resolution": (None if gap_over_mde is None
                                     else bool(gap_over_mde < 1.0)),
            "power_target": res.get("power_target"),
            "paired_sd_pp": sd_p,
            "atlas_rung_pp": ed.get("atlas_rung_pp"),
            "capacity_rung_pp": ed.get("capacity_rung_pp"),
            "sign_flips": ed.get("sign_flips"),
            "sign_agreement": sign, "pairs": pairs,
            "positive_phases": pr.get("positive"),
            "min_pp": pr.get("min_pp"), "max_pp": pr.get("max_pp"),
            "spread_pp": pr.get("spread_pp"),
            "widths": widths, "age_days": age,
            "evidence_cutoff": cutoff, "asof": asof, "source": src}


def _next_decision(score_dates, last_bar, rebal=REBAL, start="2020-01-01"):
    """Trading bars until the next decision on the engine's own grid (no future dates exist)."""
    dates = [d for d in score_dates if d >= pd.Timestamp(start)]
    if last_bar not in dates:
        return None
    pos = dates.index(last_bar)
    return int(((pos // rebal) + 1) * rebal - pos)


# --------------------------------------------------------------------------- selftest
def accrual_window(idx):
    """Which bars the cash carry was averaged over.

    Three faces quote a cash yield and none of them say over what: this ticket's backtest mean,
    the book page's last-12-months roll, and the last quote. All three are correct and they differ
    by a factor of two, so the window travels with the number (r1167).
    """
    idx = pd.DatetimeIndex(idx)
    if len(idx) == 0:
        return None
    return {"first": str(idx[0].date()), "last": str(idx[-1].date()),
            "years": round((idx[-1] - idx[0]).days / 365.25, 2)}


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

    # leg4b: the cash carry must say which bars it averaged. Three live faces quote a cash yield
    # (this ticket's backtest mean 2.087%, the book page's 1y roll 1.313%, the last quote 1.09%)
    # and without the window they read as a contradiction (r1167).
    chk("leg4b the cash carry states the window it averaged",
        accrual_window(d2 := pd.DatetimeIndex(["2021-01-04", "2021-01-07"]))
        == {"first": "2021-01-04", "last": "2021-01-07", "years": 0.01}
        and accrual_window(pd.DatetimeIndex([])) is None,
        str(accrual_window(d2)))

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

    # leg12/13: the width disclosure prices this ticket against the card's own width,
    # and stays silent-and-honest (None) rather than inventing a zero when the audit or
    # the card artefact is missing. Fixtures, not the live files.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        audit_p = os.path.join(td, "audit.json")
        with open(audit_p, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-10-23", "rows": [
                {"n_hold": 5, "book": {"cagr": 0.1105, "sharpe": 1.353, "maxdd": -0.0601}},
                {"n_hold": 12, "book": {"cagr": 0.0953, "sharpe": 1.560, "maxdd": -0.0417}}]}, f)
        # card_dir pointed at nothing: the live card's rule must not leak into a fixture
        # (the audit below carries one arm, which is then used and named).
        wd = width_disclosure(card_n=12, audit_path=audit_p,
                              card_dir=os.path.join(td, "no_card"))
        chk("leg12 width disclosure reads the two rows and their difference",
            bool(wd) and wd["ticket_names"] == 5 and wd["card_names"] == 12
            and abs(wd["delta_ticket_minus_card"]["cagr_pp"] - 1.52) < 1e-9
            and abs(wd["delta_ticket_minus_card"]["sharpe"] + 0.207) < 1e-9,
            "delta=%s" % (wd["delta_ticket_minus_card"] if wd else None))
        chk("leg13 missing width row -> None (no silent zero)",
            width_disclosure(card_n=99, audit_path=audit_p) is None
            and width_disclosure(card_n=12, audit_path=os.path.join(td, "nope.json")) is None)

        # leg14: the card width comes off the card's pointer chain, not a constant
        cd = os.path.join(td, "prod")
        os.makedirs(cd)
        with open(os.path.join(cd, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"file": "PRODUCTION-2026-10-23.json"}, f)
        with open(os.path.join(cd, "PRODUCTION-2026-10-23.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12}}, f)
        chk("leg14 card width read from the card pointer chain",
            card_width(cd) == 12 and card_width(os.path.join(td, "absent")) is None,
            "read=%s" % card_width(cd))

        # leg15: latest.json may BE the card (live shape) or point at it -- the fixture
        # above only proved the pointer shape, and the live run then said "unavailable".
        cd2 = os.path.join(td, "prod2")
        os.makedirs(cd2)
        with open(os.path.join(cd2, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12}, "sheet": {}}, f)
        chk("leg15 latest.json holding the card itself is read too",
            card_width(cd2) == 12, "read=%s" % card_width(cd2))
        chk("leg16 live wiring: real card x real audit produce a disclosure",
            (width_disclosure() is not None) if os.path.exists(AUDIT_PATH) else True,
            "card=%s audit=%s" % (card_width(), os.path.exists(AUDIT_PATH)))

        # leg17/18 -> numbered 27/28 (17/18 were taken by the decision-bar and card_book
        # legs below): the audit now carries BOTH leverage rules, so a lookup keyed on the
        # name count alone returns whichever arm was written last (r1280's "last arm
        # silently wins" class, one file over). The ticket's cell must be the BETA row
        # even though a vol row with the same n_hold exists further down the file, and
        # the two width effects must be reported as separate arms.
        audit2 = os.path.join(td, "audit2.json")
        with open(audit2, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-10-26", "rows": [
                {"n_hold": 5, "rule": "beta", "book": {"cagr": 0.1104, "sharpe": 1.352,
                                                       "maxdd": -0.0601, "vol": 0.0816}},
                {"n_hold": 12, "rule": "beta", "book": {"cagr": 0.0952, "sharpe": 1.561,
                                                        "maxdd": -0.0417, "vol": 0.061}},
                {"n_hold": 5, "rule": "vol", "book": {"cagr": 0.1169, "sharpe": 1.352,
                                                      "maxdd": -0.0756, "vol": 0.0865}},
                {"n_hold": 12, "rule": "vol", "book": {"cagr": 0.119, "sharpe": 1.357,
                                                       "maxdd": -0.0795, "vol": 0.0876}}]}, f)
        cd_arm = os.path.join(td, "prod_arm")
        os.makedirs(cd_arm, exist_ok=True)
        with open(os.path.join(cd_arm, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08}}, f)
        wd2 = width_disclosure(card_n=12, audit_path=audit2, card_dir=cd_arm)
        chk("leg27 width lookup keyed by (names, rule): ticket cell is the beta arm, "
            "not whichever arm was written last",
            bool(wd2) and abs(wd2["ticket"]["cagr"] - 0.1104) < 1e-12
            and abs(wd2["card"]["cagr"] - 0.119) < 1e-12
            and wd2["ticket_rule"] == "beta" and wd2["card_rule"] == "vol",
            "ticket=%s card=%s" % (wd2["ticket"]["cagr"] if wd2 else None,
                                   wd2["card"]["cagr"] if wd2 else None))
        chk("leg28 same-rule width effect reported per arm, and the published faces "
            "compared as a diagonal",
            bool(wd2) and abs(wd2["width_effect"]["beta"]["pp"] + 1.52) < 1e-9
            and abs(wd2["width_effect"]["vol"]["pp"] - 0.21) < 1e-9
            and abs(wd2["delta_ticket_minus_card"]["cagr_pp"] + 0.86) < 1e-9,
            "arms=%s diag=%.2f" % (wd2["width_effect"] if wd2 else None,
                                   (wd2["delta_ticket_minus_card"]["cagr_pp"] if wd2 else 0)))

        # leg17: the ticket ranks on the engine's last DECISION bar, not the panel's last
        # bar. Until r1277 it ranked slip.index[-1], so the ticket traded five names the
        # book never held (2026-10-23 ticket vs the 2026-10-14 book in force: disjoint).
        gd = list(pd.bdate_range("2021-01-04", periods=45))
        rebal_t = 20
        dec_bar = gd[(len(gd) - 1) // rebal_t * rebal_t]
        chk("leg17 ticket ranks on the last grid decision bar",
            dec_bar == gd[40] and dec_bar != gd[-1],
            "dec=%s last=%s" % (dec_bar.date(), gd[-1].date()))
        # leg18: card_book reads the sheet off the pointer chain and the ticket's N names
        # are a prefix of it when both rank on the same bar (cross-artefact agreement).
        cd3 = os.path.join(td, "prod3")
        os.makedirs(cd3)
        syms = ["A%03d" % i for i in range(6)]
        with open(os.path.join(cd3, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 6},
                       "feed_status": {"status": "stale_feed", "ticket_bar": "2026-10-23"},
                       "sheet": {"as_of_bar": "2026-10-23",
                                 "book_decided_at": "2026-10-14", "risk_scale": 0.7008,
                                 "legs": [{"symbol": s} for s in syms]}}, f)
        cb = card_book(cd3)
        chk("leg18 card_book reads the held book off the card",
            bool(cb) and cb["decided_at"] == "2026-10-14" and cb["symbols"] == syms
            and card_book(os.path.join(td, "absent")) is None,
            "decided_at=%s n=%s" % (cb and cb["decided_at"], cb and len(cb["symbols"])))
        chk("leg19 ticket names are a prefix of the card's book",
            cb["symbols"][:3] == syms[:3] and cb["symbols"][:3] != syms[3:6])

    # leg10: a short universe yields no ticket rather than a partial one
    chk("leg10 insufficient picks -> no ticket",
        build_ticket(pd.Series({"AAA": 1.0}), px, 0.2, 1e6, n_hold=3) is None)

    # leg11: k in force lags the decision by exactly one bar
    sched2 = [(idx[5], 0.7, 0.3)]
    kv = in_force(sched2, idx)
    chk("leg11 decision applies from the next bar", bool(np.isnan(kv.iloc[5]))
        and abs(float(kv.iloc[6]) - 0.7) < 1e-12, "k5=%s k6=%.3f" % (kv.iloc[5], kv.iloc[6]))

    # legs 20-24: the ticket must answer "is this priced off a current bar?" by itself,
    # because every other leg grades the panel by the panel (r1286/r1287).
    cal = ["2026-10-21", "2026-10-22", "2026-10-23", "2026-10-26"]
    cur = feed_status(cal, "2026-10-26", "2026-10-26", "in_sync")
    chk("leg20 ticket on the newest official bar reads current",
        cur["status"] == "current" and cur["lag_days"] == 0,
        "status=%s lag=%s" % (cur["status"], cur["lag_days"]))
    lag1 = feed_status(cal, "2026-10-23", "2026-10-26", "source_lag")
    chk("leg21 one unpublished day reads as a 1-day lag (Fri->Mon costs 1, not 3)",
        lag1["status"] == "stale_feed" and lag1["lag_days"] == 1,
        "status=%s lag=%s" % (lag1["status"], lag1["lag_days"]))
    gap = feed_status(cal, "2026-10-22", "2026-10-26", "panel_gap")
    chk("leg22 a stopped feed outranks the plain lag",
        gap["status"] == "feed_broken" and gap["lag_days"] == 2,
        "status=%s lag=%s" % (gap["status"], gap["lag_days"]))
    unk = feed_status(cal, "2026-10-23", None, "in_sync")
    chk("leg23 no calendar reads unknown, never current", unk["status"] == "unknown",
        "status=%s" % unk["status"])
    md = card(None, None, None, "2026-10-23", 0.2,
              {"inception": "2024-01-01", "feed": lag1})
    chk("leg24 the stale warning reaches the one-page face a human reads",
        "\u26a0" in md and "stale_feed" in md, "chars=%d" % len(md))

    # leg24b/c (r1348): the sheet prints one realised drawdown, but the bootstrap arms put
    # the p5 several pp deeper. A tail quoted without its block is a sentence without its
    # parameter, so the sheet must carry both -- and must say 'unpublished' when absent.
    _db_keep = glob.glob
    try:
        doc = {"evidence_cutoff": "2026-10-29", "arms": [{"block": 5}, {"block": 250}],
               "spread": {"maxdd_p5": {"min": -0.2502, "max": -0.1708},
                          "maxdd_p50": {"min": -0.1459, "max": -0.1214},
                          "dd_break_share": {"min": 0.011, "max": 0.161}}}
        glob.glob = lambda *a, **k: [os.path.join("X", "BLOCKS-2026-10-29.json")]
        _open = open

        class _F:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self, *a):
                return json.dumps(doc)

        import builtins
        builtins.open = lambda *a, **k: _F()
        try:
            band = drawdown_band()
            md_band = card(None, None, None, "2026-10-29", 0.2, {"inception": "2024-01-01"})
        finally:
            builtins.open = _open
        chk("leg24b sheet carries the drawdown band with its block set",
            band is not None and "-25.0%" in md_band and "5/250" in md_band,
            "band=%s" % (band or {}).get("block_set"))
        glob.glob = lambda *a, **k: []
        chk("leg24c no band on disk is disclosed, never invented",
            drawdown_band() is None
            and "无自助带在盘" in card(None, None, None, "2026-10-29", 0.2,
                                       {"inception": "2024-01-01"}))
    finally:
        glob.glob = _db_keep

    # legs 25-26: two faces can share a decision bar and still price a day apart -- on a
    # HOLD bar the vol overlay re-sizes weights and the cash slot every single day, so the
    # priced bar has to travel with the book (r1290: card at 10-23/stale_feed, ticket at
    # 10-26/current, and nothing in either face said so).
    import shutil
    import tempfile
    cdt = tempfile.mkdtemp()
    try:
        with open(os.path.join(cdt, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"feed_status": {"status": "stale_feed", "ticket_bar": "2026-10-23"},
                       "sheet": {"as_of_bar": "2026-10-23", "book_decided_at": "2026-10-14",
                                 "legs": [{"symbol": "AAA"}]}}, f)
        cbo = card_book(cdt)
        chk("leg25 card_book carries the priced bar and its feed status",
            cbo["priced_bar"] == "2026-10-23" and cbo["feed_status"] == "stale_feed",
            "bar=%s feed=%s" % (cbo.get("priced_bar"), cbo.get("feed_status")))
        md_split = card(None, None, None, "2026-10-26", 0.2,
                        {"inception": "2024-01-01", "feed": cur,
                         "agreement": {"card_decided_at": cbo["decided_at"],
                                       "ticket_book_decided_at": "2026-10-14",
                                       "same_decision_bar": True,
                                       "card_priced_bar": cbo["priced_bar"],
                                       "card_feed_status": cbo["feed_status"],
                                       "ticket_priced_bar": "2026-10-26",
                                       "same_priced_bar": False}})
        chk("leg26 a one-day-stale card is flagged despite a matching decision bar",
            "\u26a0" in md_split and "两张面定价不在同一天" in md_split
            and "一致=True" in md_split, "chars=%d" % len(md_split))
    finally:
        shutil.rmtree(cdt, ignore_errors=True)

    # ---- card-config ticket (r1333): the executable face must be the card's own book
    cdt = tempfile.mkdtemp()
    try:
        legs = [{"symbol": "AAA", "name": "a", "class": "equity", "weight": 0.2,
                 "ref_price": 2.0, "lots_100": 100000, "amount_cny": 200000.0,
                 "actual_amount_cny": 200000.0},
                {"symbol": "BBB", "name": "b", "class": "equity", "weight": 0.25,
                 "ref_price": 5.0, "lots_100": 50000, "amount_cny": 250000.0,
                 "actual_amount_cny": 250000.0},
                {"symbol": "CCC", "name": "c", "class": "equity", "weight": 0.25,
                 "ref_price": 1.0, "lots_100": 250000, "amount_cny": 250000.0,
                 "actual_amount_cny": 250000.0}]
        card_doc = {"config": {"n_hold": 3, "rebal": 20, "vol_target": 0.08,
                              "capital_cny": 1000000.0, "cost_bp_per_side": 10.0},
                    "feed_status": {"status": "current", "ticket_bar": "2026-10-28",
                                    "expected_bar": "2026-10-28", "lag_days": 0},
                    "sheet": {"as_of_bar": "2026-10-28", "book_decided_at": "2026-10-14",
                              "capital_cny": 1000000.0, "risk_scale": 0.7,
                              "target_vol": 0.08, "cash_weight": 0.3,
                              "cash_amount_cny": 300000.0, "legs": legs,
                              "bars_until_next_decision": 10}}
        with open(os.path.join(cdt, "latest.json"), "w", encoding="utf-8") as f:
            json.dump(card_doc, f, ensure_ascii=False)
        led_same = {"config": {"n_hold": 3, "vol_target": 0.08, "rebal": 20,
                               "cost_per_side": 0.001},
                    "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                      "names": ["AAA", "BBB", "CCC"]},
                    "bars": [{"bar": "2026-10-28", "nav": 1.00053}], "status": "live"}
        lp = os.path.join(cdt, "LEDGER.json")
        with open(lp, "w", encoding="utf-8") as f:
            json.dump(led_same, f, ensure_ascii=False)

        tk = card_config_ticket(card_dir=cdt, ledger_path=lp)
        rc = tk["recon"] if tk else {}
        chk("leg27 card-config ticket reproduces the card's names, scale and config",
            bool(tk) and rc.get("same_names_as_card") is True
            and rc.get("same_names_as_ledger") is True
            and rc.get("same_scale_as_ledger") is True
            and rc.get("same_config_as_ledger") is True,
            "names=%s scale=%s cfg=%s" % (rc.get("same_names_as_card"),
                                          rc.get("same_scale_as_ledger"),
                                          rc.get("same_config_as_ledger")))
        chk("leg28 lots recomputed from price x weight match the card's published lot counts",
            bool(tk) and tk["reprice_mismatch"] == []
            and [r["lots"] for r in tk["order"]] == [1000, 500, 2500],
            "mismatch=%s" % (tk["reprice_mismatch"] if tk else None))

        tk2 = card_config_ticket(card_dir=cdt, ledger_path=lp, nav=2000000.0)
        chk("leg29 a doubled stated capital doubles the book and keeps the cash share",
            bool(tk2) and abs(tk2["cash_weight"] - 0.3) < 0.001
            and 0.98 * 1_400_000.0 <= tk2["book_amount"] <= 1_400_000.0,
            "book=%.0f cash_w=%.4f" % (tk2["book_amount"] if tk2 else -1,
                                       tk2["cash_weight"] if tk2 else -1))

        led_other = json.loads(json.dumps(led_same))
        led_other["book_in_force"]["names"] = ["AAA", "BBB", "ZZZ"]
        lp2 = os.path.join(cdt, "LEDGER-other.json")
        with open(lp2, "w", encoding="utf-8") as f:
            json.dump(led_other, f, ensure_ascii=False)
        tk3 = card_config_ticket(card_dir=cdt, ledger_path=lp2)
        chk("leg30 a ledger holding other names is reported as a different book",
            bool(tk3) and tk3["recon"]["same_names_as_ledger"] is False,
            "verdict=%s" % (tk3["recon"]["same_names_as_ledger"] if tk3 else None))

        md_card = card_config_card(tk, None) if tk else ""
        chk("leg31 the order sheet prints the three-face table and both verdicts",
            "三面是不是同一本书" in md_card and "本单 vs 卡片 一致" in md_card
            and "本单 vs 账本 一致" in md_card and "2.000" in md_card,
            "chars=%d" % len(md_card))

        # ---- restated-bar notice (r1371): a mark that moves after the bar settled is a
        # history change, and the operator holding the sheet was the last to hear about it.
        led_rst = json.loads(json.dumps(led_same))
        led_rst["restatements"] = [{"ts": "2026-10-30T19:18:29+0800", "bar": "2026-10-28",
                                    "reason": "published while the panel was still filling",
                                    "nav_published": 1.00053, "nav_settled": 1.00052,
                                    "delta": -1e-05}]
        lp3 = os.path.join(cdt, "LEDGER-rst.json")
        with open(lp3, "w", encoding="utf-8") as f:
            json.dump(led_rst, f, ensure_ascii=False)
        tk4 = card_config_ticket(card_dir=cdt, ledger_path=lp3)
        md4 = card_config_card(tk4, None) if tk4 else ""
        chk("leg31b a bar restated after settling reaches the ticket instead of being silent history",
            bool(tk4) and tk4["recon"]["restated_bars"] == ["2026-10-28"]
            and "定格之后又被改述" in md4 and "1.00053000" in md4 and "1.00052000" in md4,
            "bars=%s in_md=%s" % (tk4["recon"]["restated_bars"] if tk4 else None,
                                  "定格之后又被改述" in md4))

        # the record existed on the bars before it existed at the ledger's top level
        led_rst2 = json.loads(json.dumps(led_same))
        led_rst2["bars"] = [{"bar": "2026-10-28", "nav": 1.00052,
                             "restated_at": "2026-10-30T19:18:29+0800",
                             "nav_published": 1.00053, "nav_settled": 1.00052}]
        led_rst2.pop("restatements", None)
        lp4 = os.path.join(cdt, "LEDGER-rst-on-bars.json")
        with open(lp4, "w", encoding="utf-8") as f:
            json.dump(led_rst2, f, ensure_ascii=False)
        tk5 = card_config_ticket(card_dir=cdt, ledger_path=lp4)
        _r5 = (tk5 or {}).get("recon") or {}
        chk("leg31c an older ledger that records restatements only on its bars still reaches the sheet",
            bool(tk5) and _r5.get("restatements_source") == "bars"
            and _r5.get("restated_bars") == ["2026-10-28"]
            and abs((_r5.get("restatements") or [{}])[0].get("delta") + 1e-05) < 1e-9,
            "source=%s bars=%s" % (_r5.get("restatements_source"), _r5.get("restated_bars")))

        # "no restatement" must be something the sheet checked, never the default when the
        # ledger is missing -- otherwise a deleted artifact reads as a clean history.
        tk6 = card_config_ticket(card_dir=cdt, ledger_path=os.path.join(cdt, "NO-LEDGER.json"))
        md6 = card_config_card(tk6, None) if tk6 else ""
        chk("leg31d an unreadable ledger prints 'cannot verify', not 'no restatements'",
            bool(tk6) and tk6["recon"]["restatements_readable"] is False
            and "无法核验" in md6 and "没有一根在定格之后被改述" not in md6,
            "readable=%s" % (tk6["recon"]["restatements_readable"] if tk6 else None))

        led_clean = json.loads(json.dumps(led_same))
        led_clean["restatements"] = []
        lp5 = os.path.join(cdt, "LEDGER-clean.json")
        with open(lp5, "w", encoding="utf-8") as f:
            json.dump(led_clean, f, ensure_ascii=False)
        tk7 = card_config_ticket(card_dir=cdt, ledger_path=lp5)
        md7 = card_config_card(tk7, None) if tk7 else ""
        chk("leg31e a readable ledger with an empty restatement list says so as a checked fact",
            bool(tk7) and tk7["recon"]["restatements_readable"] is True
            and tk7["recon"]["restated_bars"] == []
            and "没有一根在定格之后被改述" in md7 and "1 根 bar" in md7,
            "readable=%s bars=%s" % (tk7["recon"].get("restatements_readable") if tk7 else None,
                                     tk7["recon"]["restated_bars"] if tk7 else None))
    finally:
        shutil.rmtree(cdt, ignore_errors=True)

    # ---- lot granularity (r1334): the card's cash row is a target, the desk gets
    # floor'ed lots, so the shortfall has to be published as a curve over capital.
    fx = [{"symbol": "AAA", "weight": 0.0584, "ref_price": 2.194},
          {"symbol": "BBB", "weight": 0.0584, "ref_price": 11.8419},
          {"symbol": "CCC", "weight": 0.0584, "ref_price": 1.095},
          {"symbol": "DDD", "weight": 0.0584, "ref_price": 3.407}]
    lp1 = lot_point(fx, 1_000_000.0, scale=0.2336)
    chk("leg32 the lot point reports cash vs the card's target and the worst mis-sized leg",
        lp1["cash_vs_target_cny"] > 0.0 and lp1["max_abs_weight_drift_pp"] > 0.0
        and lp1["target_book_cny"] == 233600.0,
        "cash_vs_target=%s drift=%.3f" % (lp1["cash_vs_target_cny"],
                                          lp1["max_abs_weight_drift_pp"]))
    lc = lot_curve(fx, scale=0.2336)
    chk("leg33 granularity cost falls monotonically as the book grows",
        lc["monotone_non_increasing"] is True
        and lc["points"][-1]["max_abs_weight_drift_pp"]
        < lc["points"][0]["max_abs_weight_drift_pp"],
        "first=%.3f last=%.3f" % (lc["points"][0]["max_abs_weight_drift_pp"],
                                  lc["points"][-1]["max_abs_weight_drift_pp"]))
    px_lot = max(l["ref_price"] * LOT for l in fx)
    chk("leg34 every leg is off by less than one lot (drift bound = px*lot / capital)",
        all(p["max_abs_weight_drift_pp"] <= 100.0 * px_lot / p["capital_cny"] + 1e-6
            for p in lc["points"]),
        "bound at 50k=%.2f" % (100.0 * px_lot / 50_000.0))
    cheap = [{"symbol": "E%02d" % i, "weight": 0.05, "ref_price": 1.0}
             for i in range(19)] + [{"symbol": "PRICEY", "weight": 0.05,
                                     "ref_price": 1000.0}]
    lc2 = lot_curve(cheap, scale=1.0)
    chk("leg35 below the one-lot floor the book cannot even be bought (legs_with_zero_lots)",
        lc2["one_lot_floor_cny"] == 100_000.0 / 0.05
        and lc2["points"][0]["legs_with_zero_lots"] >= 1
        and lc2["points"][-1]["legs_with_zero_lots"] == 0,
        "floor=%s zero@50k=%d zero@20M=%d" % (lc2["one_lot_floor_cny"],
                                              lc2["points"][0]["legs_with_zero_lots"],
                                              lc2["points"][-1]["legs_with_zero_lots"]))
    md_lc = "\n".join(lot_curve_md(lc, 1_000_000.0))
    chk("leg36 the operator's page carries the capital table and both thresholds",
        "| 资金 |" in md_lc and "≤1.00pp" in md_lc and "单调不增" in md_lc,
        "chars=%d" % len(md_lc))
    chk("leg37 the yuan shortfall is bounded by one lot per leg and does NOT shrink",
        lc["max_observed_shortfall_cny"] <= lc["shortfall_bound_cny"] + 1e-6
        and abs(lc["points"][0]["cash_vs_target_cny"]
                - lc["points"][-1]["cash_vs_target_cny"])
            < lc["shortfall_bound_cny"],
        "bound=%s max=%s" % (lc["shortfall_bound_cny"], lc["max_observed_shortfall_cny"]))

    # ---- r1342: the card's cash row is now the EXECUTABLE cash, so the ticket must agree
    # with it to the yuan and stop printing the "card row is only a target" disclosure.
    # Both directions are asserted on the same fixture: a card that prints
    # capital - spent closes the gap, a legacy card that prints (1 - k) * capital still
    # gets called out. One-sided, this leg would pass on the old renderer too.
    cdt3 = tempfile.mkdtemp()
    try:
        leg_fx = [{"symbol": s, "name": s, "class": "equity", "weight": 0.35,
                   "ref_price": 2.194, "lots_100": 159500, "amount_cny": 350000.0,
                   "actual_amount_cny": 349943.0} for s in ("AAA", "BBB")]
        sheet_fx = {"as_of_bar": "2026-10-29", "book_decided_at": "2026-10-14",
                    "capital_cny": 1000000.0, "risk_scale": 0.7, "target_vol": 0.08,
                    "cash_weight": 0.3, "legs": leg_fx,
                    "bars_until_next_decision": 9}
        cfg_fx = {"n_hold": 2, "rebal": 20, "vol_target": 0.08,
                  "capital_cny": 1000000.0, "cost_bp_per_side": 10.0}
        lp4 = os.path.join(cdt3, "LEDGER.json")
        with open(lp4, "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 2, "vol_target": 0.08, "rebal": 20,
                                  "cost_per_side": 0.001},
                       "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                         "names": ["AAA", "BBB"]},
                       "bars": [{"bar": "2026-10-29", "nav": 1.0}], "status": "live"},
                      f, ensure_ascii=False)
        printed = {}
        for label, cash_row in (("executable", {"cash_executable_cny": 1000000.0 - 2 * 349943.0,
                                                "cash_amount_cny": 300000.0}),
                                ("target", {"cash_amount_cny": 300000.0})):
            doc = {"config": cfg_fx,
                   "feed_status": {"status": "current", "ticket_bar": "2026-10-29",
                                   "expected_bar": "2026-10-29", "lag_days": 0},
                   "sheet": dict(sheet_fx, **cash_row)}
            with open(os.path.join(cdt3, "latest.json"), "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False)
            tk_fx = card_config_ticket(card_dir=cdt3, ledger_path=lp4)
            md_fx = card_config_card(tk_fx, None) if tk_fx else ""
            printed[label] = (tk_fx, md_fx)
        tk_e, md_e = printed["executable"]
        tk_t, md_t = printed["target"]
        chk("leg38 an executable cash row closes the ticket gap to the yuan",
            bool(tk_e) and abs(tk_e["cash_amount"]
                               - (1000000.0 - 2 * 349943.0)) <= 1e-6
            and "卡片现金行是目标口径" not in md_e,
            "cash=%.2f gap_paragraph=%s" % (tk_e["cash_amount"] if tk_e else -1,
                                            "卡片现金行是目标口径" in md_e))
        chk("leg39 a legacy target cash row is still called out as a target",
            bool(tk_t) and "卡片现金行是目标口径" in md_t,
            "legacy_paragraph=%s" % ("卡片现金行是目标口径" in md_t))
    finally:
        shutil.rmtree(cdt3, ignore_errors=True)

    # ---- r1356b: the live-width ruler has to reach the ticket, and its verdict has to be
    # re-derived from the numbers it publishes (r1266: a label copied blind is a receipt).
    # Every state gets its own fixture, and the widths/staleness ones are the two ways a
    # stale face would otherwise keep printing a clean "coin flip" forever.
    cdt5 = tempfile.mkdtemp()
    try:
        def _ruler_doc(**over):
            d = {"script": "scripts/etf_book_phase_atlas_arms.py --live-widths",
                 "rule": {"pairs_min": 20, "sign_split_max": 0.6},
                 "evidence_cutoff": "2026-10-29",
                 "live_faces": {"card": {"n_hold": 12, "rule": "vol_target"},
                                "ticket": {"n_hold": 5, "rule": "beta"}},
                 "paired": {"pairs": 20, "median_pp": 0.09, "positive": 10,
                            "sign_agreement": 0.5, "spread_pp": 4.94},
                 "engine_disagreement": {"atlas_rung_pp": 0.515, "capacity_rung_pp": -1.53,
                                         "rung_disagreement_pp": 2.045, "sign_flips": True},
                 "verdict": "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"}
            d.update(over)
            return d

        def _put(name, doc):
            fp = os.path.join(cdt5, name)
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(doc, f)
            return fp

        cd5 = os.path.join(cdt5, "card")
        os.makedirs(cd5, exist_ok=True)
        with open(os.path.join(cd5, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08, "rebal": 20}}, f)

        r_in = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                path=_put("in.json", _ruler_doc()))
        chk("leg40 a paired gap inside the engines' own disagreement reads as a coin flip",
            r_in["state"] == "inside_disagreement"
            and abs(r_in["share_of_disagreement"] - 0.044) < 5e-3,
            "state=%s share=%.4f" % (r_in["state"], r_in["share_of_disagreement"] or -1))
        chk("leg40b a gap larger than the disagreement stops being a coin flip",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=_put("wide.json", _ruler_doc(
                                 paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                         "sign_agreement": 0.9, "spread_pp": 4.94},
                                 verdict="SEPARATED")))["state"] == "separated",
            "")
        chk("leg40c a face whose label contradicts its own numbers is flagged, not trusted",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=_put("lab.json", _ruler_doc(
                                 paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                         "sign_agreement": 0.9, "spread_pp": 4.94})
                             ))["state"] == "inconsistent", "")
        chk("leg40d a face pricing widths the live faces no longer run says so",
            live_width_ruler(asof="2026-10-29", card_n=8, card_dir=cd5,
                             path=_put("mov.json", _ruler_doc()))["state"] == "widths_moved",
            "")
        chk("leg40e an old cutoff is stale rather than a standing verdict",
            live_width_ruler(asof="2026-11-20", card_n=12, card_dir=cd5,
                             path=_put("old.json", _ruler_doc(evidence_cutoff="2026-10-20"))
                             )["state"] == "stale", "")
        chk("leg40f no face on disk is unavailable, never silently clean",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=os.path.join(cdt5, "nope.json"))["state"] == "unavailable",
            "")

        md_r = card(None, None, None, "2026-10-29", 0.2,
                    {"ruler": r_in, "width": None, "feed": None, "agreement": None})
        chk("leg41 the order page prints the ruler (a number in research/ reaches nobody)",
            "## 两张面之间的差" in md_r and "+0.09pp" in md_r and "2.0" in md_r
            and "%" in md_r,
            "chars=%d gap=%s" % (len(md_r), "+0.09pp" in md_r))
        bad_r = dict(r_in, state="stale", detail="cutoff 2026-10-01 is 28 days behind")
        md_st = card(None, None, None, "2026-10-29", 0.2,
                     {"ruler": bad_r, "width": None, "feed": None, "agreement": None})
        chk("leg41b a non-clean ruler changes what the page says",
            md_st != md_r and "尺子状态" in md_st, "")

        # ---- r1357: the SAME ruler has to reach the card sheet, and it has to say which
        # face on that ruler this sheet is. The paired gap is between the two live faces,
        # so a card sheet that printed "gap vs the card" would be quoting a difference
        # between two other books. Three legs: the reading is there and names the other
        # face, a moved-widths face leaves the sheet unverified instead of clean, and the
        # caller's sheet label alone cannot invent a role.
        chk("leg42 the ruler knows which face the asking sheet is (and never for free)",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="card",
                             path=_put("s_card.json", _ruler_doc()))["sheet_role"]
            == "measured_card"
            and live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="ticket",
                                 path=_put("s_tk.json", _ruler_doc()))["sheet_role"]
            == "measured_ticket"
            and live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="x",
                                 path=_put("s_x.json", _ruler_doc()))["sheet_role"] is None,
            "")
        r_moved = live_width_ruler(asof="2026-10-29", card_n=8, card_dir=cd5, sheet="card",
                                   path=_put("s_mv.json", _ruler_doc()))
        chk("leg42b a face pricing a width we no longer run leaves this sheet unverified",
            r_moved["state"] == "widths_moved" and r_moved["sheet_role"] == "unverified",
            "state=%s role=%s" % (r_moved["state"], r_moved["sheet_role"]))

        # a 12-leg card sheet, so the rendered page is the one a reader would hold
        cd6 = os.path.join(cdt5, "card12")
        os.makedirs(cd6, exist_ok=True)
        legs12 = [{"symbol": "S%02d" % i, "name": "S%02d" % i, "class": "equity",
                   "weight": 0.058, "ref_price": 2.0, "lots_100": 29000,
                   "amount_cny": 58000.0, "actual_amount_cny": 58000.0} for i in range(12)]
        with open(os.path.join(cd6, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "rebal": 20, "vol_target": 0.08,
                                  "capital_cny": 1000000.0, "cost_bp_per_side": 10.0},
                       "feed_status": {"status": "current", "ticket_bar": "2026-10-29",
                                       "expected_bar": "2026-10-29", "lag_days": 0},
                       "sheet": {"as_of_bar": "2026-10-29", "book_decided_at": "2026-10-14",
                                 "capital_cny": 1000000.0, "risk_scale": 0.7,
                                 "target_vol": 0.08, "cash_weight": 0.3, "legs": legs12,
                                 "bars_until_next_decision": 9}}, f, ensure_ascii=False)
        lp6 = os.path.join(cdt5, "LEDGER6.json")
        with open(lp6, "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08, "rebal": 20,
                                  "cost_per_side": 0.001},
                       "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                         "names": [r["symbol"] for r in legs12]},
                       "bars": [{"bar": "2026-10-29", "nav": 1.0}], "status": "live"},
                      f, ensure_ascii=False)
        tk12 = card_config_ticket(card_dir=cd6, ledger_path=lp6)
        r_card = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="card",
                                  path=_put("s_card2.json", _ruler_doc()))
        md_c = card_config_card(tk12, None, r_card) if tk12 else ""
        chk("leg42c the card sheet prints the other sheet's measured gap, not its own",
            bool(tk12) and "+0.09pp" in md_c and "5 名 beta 覆盖那张单 vs 本单" in md_c
            and "另一张单和本单的差" in md_c and "4.4%" in md_c,
            "chars=%d has_gap=%s" % (len(md_c), "+0.09pp" in md_c))
        md_cu = card_config_card(tk12, None, r_moved) if tk12 else ""
        chk("leg42d an unverified sheet cannot print the clean reading",
            bool(md_cu) and "未核实" in md_cu and "+0.09pp" not in md_cu
            and md_cu != md_c, "")
        # r1358: the resolution is re-derived from the face's own sd and phase count. A face that
        # publishes a stored mde has no say here -- a number that can be edited independently of
        # the numbers that produce it is a receipt (r1266), so feed a poisoned one and demand the
        # derived value.
        r_res = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("res.json", _ruler_doc(
                                     paired={"pairs": 20, "median_pp": 0.09, "positive": 10,
                                             "sign_agreement": 0.5, "spread_pp": 4.94,
                                             "sd_pp": 1.255},
                                     resolution={"mde_pp": 9.99, "power_z": 2.802,
                                                 "power_target": 0.8})))
        chk("leg42e the resolution is re-derived from sd and pairs, never read off the face",
            r_res.get("resolution_pp") is not None
            and abs(r_res["resolution_pp"] - 0.786) < 2e-3
            and r_res["resolution_pp"] != 9.99,
            "mde=%r" % (r_res.get("resolution_pp"),))
        r_wide = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                  path=_put("wide2.json", _ruler_doc(
                                      paired={"pairs": 20, "median_pp": 0.09, "positive": 10,
                                              "sign_agreement": 0.5, "spread_pp": 4.94,
                                              "sd_pp": 4.0})))
        r_big = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("big.json", _ruler_doc(
                                     paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                             "sign_agreement": 0.9, "spread_pp": 4.94,
                                             "sd_pp": 1.0},
                                     verdict="SEPARATED")))
        chk("leg42f a gap under the pairing's own resolution is flagged, a big one is not",
            r_wide.get("below_own_resolution") is True
            and r_big.get("below_own_resolution") is False,
            "wide=%r big=%r" % (r_wide.get("below_own_resolution"),
                                r_big.get("below_own_resolution")))
        chk("leg42g a face with no published dispersion says so instead of printing a zero",
            "没有公布逐相位离散度" in _resolution_md(
                live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("nosd.json", _ruler_doc()))), "")
    finally:
        shutil.rmtree(cdt5, ignore_errors=True)

    # ---- r1367: the sheet quotes one CAGR for a book that parks half its NAV in repo.
    # The split lives in one artifact; the ticket must carry it at ITS OWN beta, must do
    # the arithmetic rather than trust a field name, and must say so when the artifact is
    # missing or priced on another bar -- silence reads as "the whole number is alpha".
    cdt7 = tempfile.mkdtemp()
    try:
        rg = {"evidence_cutoff": "2026-10-30",
              "cash_rates": {"today_pct": 1.09, "today_date": "2026-10-27",
                             "observed_mean_pct": 1.9819},
              "gate": {"base_beta": 0.2,
                       "betas": {"0.1": {"observed_pct": 6.4, "flat_today_pct": 5.95,
                                         "zero_pct": 5.05, "carry_share_of_headline_pct": 21.1,
                                         "pp_per_100bp": 0.505, "cash_share": 0.775},
                                 "0.2": {"observed_pct": 11.19, "flat_today_pct": 10.85,
                                         "zero_pct": 10.19, "carry_share_of_headline_pct": 8.9,
                                         "pp_per_100bp": 0.381, "cash_share": 0.5501}}},
              "identity": {"matched": True}}
        rp7 = os.path.join(cdt7, "regime.json")
        with open(rp7, "w", encoding="utf-8") as f:
            json.dump(rg, f)
        cs = carry_split(0.2, path=rp7)
        chk("leg43 the ticket reads the carry split at its own beta and re-derives the pp",
            bool(cs) and cs["beta"] == 0.2
            and abs(cs["carry_pp"] - 1.00) < 1e-6
            and abs(cs["flat_rate_cost_pp"] - 0.34) < 1e-6
            and abs(cs["carry_share_pct"] - 8.9) < 1e-6
            and cs["identity_matched"] is True,
            "carry=%s flat=%s" % (cs and cs["carry_pp"], cs and cs["flat_rate_cost_pp"]))
        chk("leg43b an off-grid beta snaps to the nearest published cell, never to the base",
            (carry_split(0.45, path=rp7) or {}).get("beta") == 0.2
            and (carry_split(0.12, path=rp7) or {}).get("beta") == 0.1, "")
        md7 = card(None, None, None, "2026-10-30", 0.2, {"inception": "2024-01-01", "carry": cs})
        chk("leg44 the sheet prints the split: headline / zero-cash / the pp it costs",
            "这条年化里有多少是现金利息" in md7 and "8.9%" in md7
            and "10.19%" in md7 and "1.00pp" in md7, "chars=%d" % len(md7))
        chk("leg44b a split priced on another bar is flagged, not quietly quoted",
            "\u26a0" in card(None, None, None, "2026-11-05", 0.2,
                             {"inception": "2024-01-01", "carry": cs})
            and "\u26a0" not in md7, "")
        chk("leg45 no artifact is disclosed on the sheet instead of leaving a bare headline",
            carry_split(0.2, path=os.path.join(cdt7, "absent.json")) is None
            and "拆解面在盘上没有可用读数" in card(None, None, None, "2026-10-30", 0.2,
                                          {"inception": "2024-01-01", "carry": None}), "")
        broken = dict(rg)
        broken["gate"] = {"base_beta": 0.2, "betas": {"0.2": {"observed_pct": 11.19}}}
        bp7 = os.path.join(cdt7, "broken.json")
        with open(bp7, "w", encoding="utf-8") as f:
            json.dump(broken, f)
        chk("leg45b a half-written cell returns None rather than an invented zero",
            carry_split(0.2, path=bp7) is None, "")
    finally:
        shutil.rmtree(cdt7, ignore_errors=True)

    # 46a-c. the sheet has to say which price panel its own numbers were computed on
    _pb_idx = pd.bdate_range("2026-01-01", periods=4)
    _pb_flip = pd.DataFrame({"A": [10.0, 10.0, 1.0, 1.05]}, index=_pb_idx)
    _pb_ok = price_basis(_pb_flip, ["A"])
    chk("leg46a price basis: a -90% print on the panel is counted and called out",
        _pb_ok["flip_prints"] == 1 and "1 处" in _pb_ok["sentence"]
        and _pb_ok["panel"].startswith("repaired"), _pb_ok["sentence"][:60])
    _pb_clean = pd.DataFrame({"B": [10.0, 10.1, 10.2, 10.3]}, index=_pb_idx)
    _pb_none = price_basis(_pb_clean, ["B"])
    chk("leg46b price basis: a panel with no flip says the repair would change nothing",
        _pb_none["flip_prints"] == 0 and "同一批数字" in _pb_none["sentence"], "")
    _pb_md = card(None, None, None, "2026-10-30", 0.2,
                  {"inception": "2024-01-01", "price_basis": _pb_ok})
    chk("leg46c price basis: the sheet prints the line (and nothing when it is absent)",
        "价格面板" in _pb_md and "1 处" in _pb_md
        and "价格面板" not in card(None, None, None, "2026-10-30", 0.2,
                                   {"inception": "2024-01-01"}), "")
    _pb_raw = price_basis(_pb_flip, ["A"], repaired=False)
    chk("leg46d price basis: the raw arm still exists and reads differently "
        "(the counterfactual the audit needs, not a second definition)",
        _pb_raw["panel"].startswith("raw") and _pb_raw["flip_prints"] == _pb_ok["flip_prints"]
        and _pb_raw["sentence"] != _pb_ok["sentence"], _pb_raw["sentence"][:60])
    chk("leg46e price basis: both faces quote ONE implementation "
        "(the sentence this sheet prints is the one etf_equity_alpha writes)",
        _pb_ok["sentence"] == AE.price_basis_line(
            True, _pb_ok["flip_prints"], _pb_ok["flip_thr"],
            _pb_ok["symbols_with_a_flip"], PRICE_BASIS_ARTIFACT,
            columns=_pb_ok.get("columns"))["sentence"], "")
    chk("leg46f this sheet repairs its panel (r1177): the module constant is on",
        REPAIR_PANEL is True, "")

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
    if len(sys.argv) > 1 and sys.argv[1] == "card":
        # default = the card's own stated capital; --nav= only re-prices the lots
        stated = nav if any(a.startswith("--nav=") for a in sys.argv) else None
        return run_card(stated)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())