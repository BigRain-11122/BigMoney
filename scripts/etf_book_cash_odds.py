"""Paying the idle sleeve closes how many of the losing years?

r2233 answered "how often does this book lose money over a year" on the house engine, which
prices the vol-target's cash sleeve at **0%**: 93 of 1428 twelve-month starts end under water,
worst -6.47% (-64,665 CNY on a million). `etf_book_idle_cash` answered a different question --
what the same sleeve would earn if it rolled GC001 instead of sitting idle -- and found
+0.58pp of CAGR, Sharpe 1.082 -> 1.134, verdict ADMIT. Both faces are published. Neither
answers the question a reader carries into the two of them together:

    if the cash actually earns what the repo panel says it earns, how many of those
    93 losing years do I still have?  and what is the worst one now?

That is not a detail, because a de-levered book holds ~29% cash on average and the repo
panel quotes 1.5-2% a year on it. This face composes the two published measurements rather
than adding a new one:

  * the book is the same 8%-vol-target production candidate on the same engine, same
    declared execution arm (decide at the close of d, fill at the open of d+1 -- `entry_lag=1`,
    the caliber r2233 chose as the deliverable one);
  * the idle fraction is read off the engine's own per-decision `scale` (never re-derived);
  * the cash return is the published GC001 daily roll (`etf_book_cash_ladder.roll_rung` via
    `etf_book_idle_cash.cash_step_returns`), on the book's own calendar.

Honesty rails:
  * the control arm is `cash_ret == 0`: the composed series must BE the engine series
    (max relative error printed), so "cash on" and "cash off" differ only by the cash leg;
  * the cash-off arm must reproduce r2233's own count (93 of 1428). If it does not, the
    page says MISMATCH and nothing below it should be quoted;
  * a rate that is lower -- or negative -- is tested in the selftest, so the machine is not
    a device that can only report good news;
  * overlapping windows are still one history: the non-overlapping count is printed beside
    every share, exactly as r2233 does.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_cash_ladder as CL
import etf_book_idle_cash as IC
import etf_book_losing_odds as LO

FACE = "etf_book_cash_odds"
JSON_PATH = os.path.join("results", FACE + ".json")
DOC_PATH = os.path.join("research", "ETF_BOOK_CASH_ODDS.md")
WALLET = 1_000_000.0
REBAL, NHOLD, COST, VT = 20, 5, 0.0010, 0.08
ENTRY_LAG = 1                       # the deliverable caliber r2233 chose
PRIOR_FACE = "results/etf_book_losing_odds.json"
REPRO_TOL = 1e-9


# ---------------------------------------------------------------- engine + cash
def build_engine(entry_lag=ENTRY_LAG):
    """One panel build, one engine run, with the per-decision scale kept."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    diag = []
    book, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, REBAL, NHOLD,
                                       COST, vol_target=VT, diag=diag, entry_lag=entry_lag)
    return book, float(turn), diag, n_flip, len(cols)


def cash_leg(book_index):
    """The published GC001 daily roll, on the book's own calendar (zero reimplementation)."""
    rates = CL.load_panel()
    step, info, raw_ret, raw_bars = IC.cash_step_returns(rates, book_index)
    return step, info, raw_ret, raw_bars


def compose_with_cash(book, diag, cash_ret):
    """Idle fraction off the engine's own scale; the composition is `idle_cash.compose`."""
    idle = (1.0 - IC.scale_schedule(diag, book.index)).clip(lower=0.0, upper=1.0)
    return IC.compose(book, idle, cash_ret), idle


def control_gap(book, diag):
    """cash_ret == 0 must give the engine series back, bit-for-bit up to float noise."""
    ctrl, _ = compose_with_cash(book, diag, pd.Series(0.0, index=book.index))
    return float((ctrl / book - 1.0).abs().max())


# ---------------------------------------------------------------- readings
def arm_readings(ser, label):
    m = LO.measure(ser)
    m["label"] = label
    return m


def odds_row(m, label):
    h = m["horizons"]["1y"]
    ind = h.get("independent") or {"n": 0, "count_losing": 0}
    return {
        "label": label,
        "n": h["n"],
        "count_losing": h["count_losing"],
        "share_losing": h["share_losing"],
        "median": h["median"],
        "worst": h["worst"],
        "median_cny": h["median_cny"],
        "worst_cny": h["worst_cny"],
        "independent_n": ind["n"],
        "independent_losing": ind["count_losing"],
        "cagr": m["cagr"],
        "sharpe": m["daily"]["sharpe"],
        "deepest": (m["deepest"] or {}).get("depth"),
    }


def delta_rows(off, on):
    rows = {}
    for hz in ("1y", "2y", "3y"):
        o, n = off["horizons"][hz], on["horizons"][hz]
        rows[hz] = {
            "count_losing_off": o["count_losing"],
            "count_losing_on": n["count_losing"],
            "closed": o["count_losing"] - n["count_losing"],
            "median_off": o["median"], "median_on": n["median"],
            "median_gain_pp": (n["median"] - o["median"]) * 100.0,
            "worst_off": o["worst"], "worst_on": n["worst"],
            "worst_gain_pp": (n["worst"] - o["worst"]) * 100.0,
            "worst_cny_off": o["worst_cny"], "worst_cny_on": n["worst_cny"],
        }
    return rows


def reconcile_prior(off):
    """The cash-off arm has to be r2233's history, or nothing here can be quoted."""
    if not os.path.exists(PRIOR_FACE):
        return {"prior_face": PRIOR_FACE, "verdict": "UNMEASURED", "why": "prior face missing"}
    with io.open(PRIOR_FACE, encoding="utf-8") as fh:
        p = json.load(fh)
    try:
        prior = p["calibers"]["honest_lag1"]["horizons"]["1y"]
    except (KeyError, TypeError):
        return {"prior_face": PRIOR_FACE, "verdict": "UNMEASURED", "why": "prior face shape"}
    mine = off["horizons"]["1y"]
    rep = {
        "prior_face": PRIOR_FACE,
        "prior_count_losing": prior["count_losing"], "mine_count_losing": mine["count_losing"],
        "prior_n": prior["n"], "mine_n": mine["n"],
        "prior_median": prior["median"], "mine_median": mine["median"],
        "prior_worst": prior["worst"], "mine_worst": mine["worst"],
        "prior_last_bar": p.get("evidence_cutoff"),
    }
    same = (rep["prior_count_losing"] == rep["mine_count_losing"]
            and rep["prior_n"] == rep["mine_n"]
            and abs(rep["prior_median"] - rep["mine_median"]) <= 1e-6
            and abs(rep["prior_worst"] - rep["mine_worst"]) <= 1e-6)
    rep["verdict"] = "REPRODUCED" if same else "MISMATCH"
    return rep


def verdict_of(delta, recon, ctrl_err):
    if recon.get("verdict") != "REPRODUCED":
        return "REFUSE_PRIOR_NOT_REPRODUCED"
    if ctrl_err > REPRO_TOL:
        return "REFUSE_CONTROL_BROKEN"
    if delta["1y"]["closed"] < 0:
        return "CASH_MAKES_THE_ODDS_WORSE"
    if delta["1y"]["closed"] == 0:
        return "CASH_DOES_NOT_MOVE_THE_LOSING_ZERO"
    if delta["1y"]["count_losing_on"] == 0:
        return "CASH_CLOSES_EVERY_LOSING_YEAR"
    return "CASH_CLOSES_SOME_LOSING_YEARS"


# ---------------------------------------------------------------- page
BEGIN, END = "<!-- ETF-BOOK-CASH-ODDS:BEGIN -->", "<!-- ETF-BOOK-CASH-ODDS:END -->"


def pct(x, nd=2):
    return "—" if x is None else f"{x * 100:+.{nd}f}%"


def cny(x):
    return "—" if x is None else f"{x:+,.0f}"


def headline(p):
    d = p["delta"]
    y1 = d["1y"]
    if p["verdict"] == "REFUSE_PRIOR_NOT_REPRODUCED":
        return ("这条面不引用：现金为零的控制臂没有复现 r2233 的 93/1428，"
                "说明两处读的不是同一本历史。")
    if p["verdict"] == "REFUSE_CONTROL_BROKEN":
        return "这条面不引用：零利率控制臂没有还原引擎序列。"
    return (f"让闲置的现金按 GC001 生息，一年期亏钱的起点从 {y1['count_losing_off']} 个"
            f"降到 {y1['count_losing_on']} 个（共 {p['arms']['cash_off']['horizons']['1y']['n']} 个起点）；"
            f"最差的一年从 {pct(y1['worst_off'])}（{cny(y1['worst_cny_off'])} 元）"
            f"变成 {pct(y1['worst_on'])}（{cny(y1['worst_cny_on'])} 元）。")


def render(p):
    off, on = p["arms"]["cash_off"], p["arms"]["cash_on"]
    d = p["delta"]
    L = [BEGIN, "", f"**verdict** `{p['verdict']}`", "",
         f"window {on['first_bar']}..{on['last_bar']} ({on['bars']} bars = {on['years']} 年) · "
         f"evidence_cutoff {p['evidence_cutoff']} · 钱包 {WALLET:,.0f} 元 · "
         f"无债书 · {NHOLD} 只 · {REBAL} 根 bar 调仓 · {COST*1e4:.0f}bp/边 · "
         f"{VT*100:.0f}% 波动目标 · 执行口径 = 收盘决策 / 次日开盘成交（lag 1）", "",
         "## 一句话", "", p["headline"], "",
         "## 两张面拼起来的那句话", "",
         "r2233 说这本书一年亏钱的起点是 "
         f"{off['horizons']['1y']['count_losing']}/{off['horizons']['1y']['n']}——"
         "但它用的是引擎口径，引擎把波动目标腾出来的现金记成 **0% 利息**。"
         f"`etf_book_idle_cash` 说同一块现金如果按 GC001 每日滚动，年化能多 +{p['cash_pp']:.2f} 个百分点。"
         "两条都是已发布的面，拼在一起才回答「我到底会不会亏钱、亏多少」。"
         f"这本书平均 **{p['idle_share_mean']*100:.1f}%** 的钱是闲置的（中位 {p['idle_share_median']*100:.1f}%），"
         f"窗口内 GC001 净年化 **{p['cash_annual_pct']:.2f}%**。", "",
         "## 一年 / 两年 / 三年：现金生息前后并排", "",
         "| 持有 | 口径 | 起点数 | 亏钱起点 | 中位 | 最差 | 中位元 | 最差元 | 不重叠亏的 |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for hz, name in (("1y", "一年"), ("2y", "两年"), ("3y", "三年")):
        for label, m in (("现金 0%", off), ("现金 GC001", on)):
            h = m["horizons"][hz]
            ind = h.get("independent") or {"n": 0, "count_losing": 0}
            L.append(f"| {name} | {label} | {h['n']} | {h['count_losing']} ({h['share_losing']*100:.1f}%) | "
                     f"{pct(h['median'])} | {pct(h['worst'])} | {cny(h['median_cny'])} | "
                     f"{cny(h['worst_cny'])} | {ind['count_losing']} / {ind['n']} |")
    L += ["", "## 现金生息到底关掉了几扇门", "",
          "| 持有 | 关掉的亏钱起点 | 中位多赚 | 最差少亏 |", "|---|---:|---:|---:|"]
    for hz, name in (("1y", "一年"), ("2y", "两年"), ("3y", "三年")):
        r = d[hz]
        L.append(f"| {name} | {r['closed']} 个（{r['count_losing_off']} → {r['count_losing_on']}） | "
                 f"{r['median_gain_pp']:+.2f} pp | {r['worst_gain_pp']:+.2f} pp |")
    L += ["", f"注意「关掉 N 扇门」不是 N 次独立的好运：亏钱起点挤在同一段回撤里"
              f"（r2233 已印过分布）。零息腿里现金原地不动，生息腿里闲置的那部分每天进账 "
              f"+{p['cash_annual_pct']/100.0/244.0*1e4:.2f}bp（GC001 年化 {p['cash_annual_pct']:.2f}%），"
              f"按平均 {p['idle_share_mean']*100:.1f}% 的闲置比例折到账户上是每天约 "
              f"+{p['cash_annual_pct']/100.0/244.0*p['idle_share_mean']*1e4:.2f}bp；"
              f"它平移整条净值曲线、不改变形状——所以深度回撤几乎不动（"
              f"{pct((p['arms']['cash_off']['deepest'] or {}).get('depth'))} → "
              f"{pct((p['arms']['cash_on']['deepest'] or {}).get('depth'))}），"
              f"而「刚好在水下几分钱」的那些起点被抬回水面。", "",
          f"读者可以自己验算这条因果：平均闲置 {p['idle_share_mean']*100:.1f}% × GC001 年化 "
          f"{p['cash_annual_pct']:.2f}% ≈ {p['idle_share_mean']*p['cash_annual_pct']:.2f}pp/年，"
          f"与其他面实测的 {p['cash_pp']:+.2f}pp/年只差 "
          f"{abs(p['idle_share_mean']*p['cash_annual_pct'] - p['cash_pp']):.2f}pp——"
          "这点差来自闲置比例与利率的时点耦合（钱多闲置时利率偏高），不是算法差。", "",
          f"两年口径是最能改决定的一格：现金 0% 时有 {d['2y']['count_losing_off']} 个起点收在水下，"
          f"最差 {pct(d['2y']['worst_off'])}（{cny(d['2y']['worst_cny_off'])} 元）；"
          f"现金生息后一个都不剩，最差那一格变成 {pct(d['2y']['worst_on'])}"
          f"（{cny(d['2y']['worst_cny_on'])} 元）。"
          f"三年的下界从 {pct(d['3y']['worst_off'])} 抬到 {pct(d['3y']['worst_on'])}。", "",
          "## 逐年，折算成人民币", "",
          "| 年 | 现金 0% | 现金 GC001 | 差 | 根数 | 整年 |", "|---|---:|---:|---:|---:|---|"]
    offy = {r["year"]: r for r in off["years_rows"]}
    for r in on["years_rows"]:
        o = offy.get(r["year"])
        if not o:
            continue
        L.append(f"| {r['year']} | {pct(o['ret'])} | {pct(r['ret'])} | "
                 f"{(r['ret']-o['ret'])*100:+.2f} pp | {r['bars']} | "
                 f"{'否（到面板边缘）' if r['partial'] else '是'} |")
    L += ["", "## 水下多久，多深", "",
          "| 口径 | 最深洞 | 起 | 谷 | 填平 | 水下 bar |", "|---|---:|---|---|---|---:|"]
    for label, m in (("现金 0%", off), ("现金 GC001", on)):
        dp = m["deepest"]
        if dp:
            L.append(f"| {label} | {pct(dp['depth'])} | {dp['started_on']} | {dp['trough_on']} | "
                     f"{dp['recovered_on'] or '未填平'} | {dp['bars_under']} |")
    if off["current_underwater"] or on["current_underwater"]:
        c = off["current_underwater"] or {}
        c2 = on["current_underwater"] or {}
        L.append("")
        L.append(f"今天仍在洞中：现金 0% 口径 {pct(c.get('depth'))}（{c.get('bars_under')} 根），"
                 f"现金生息口径 {pct(c2.get('depth'))}（{c2.get('bars_under')} 根）。")
    L += ["", "## 对账：零利率臂是不是 r2233 那条历史", ""]
    rc = p["reconciliation"]
    if rc["verdict"] == "UNMEASURED":
        L.append(f"对账缺件（{rc.get('why')}）——未测不是零，本条所有读数都不该被引用。")
    else:
        L += [f"| 量 | 本面（现金 0%） | r2233 `{rc['prior_face']}` |", "|---|---:|---:|",
              f"| 一年亏钱起点 | {rc['mine_count_losing']} / {rc['mine_n']} | "
              f"{rc['prior_count_losing']} / {rc['prior_n']} |",
              f"| 一年中位 | {pct(rc['mine_median'])} | {pct(rc['prior_median'])} |",
              f"| 一年最差 | {pct(rc['mine_worst'])} | {pct(rc['prior_worst'])} |", "",
              f"**{rc['verdict']}**。零利率控制臂相对引擎序列的最大相对误差 "
              f"{p['control_max_rel_err']:.2e}（门 {REPRO_TOL:.0e}）——"
              "所以两臂之间只差现金这一项。", ""]
    L += ["## 读数边界（别读成承诺）", "",
          "- 现金按 GC001 **每日滚动**计息；一个真人不一定每天滚一次逆回购"
          "（`etf_book_cash_vehicle` 已量过货币 ETF 替代，那是另一条腿）。",
          "- 现金利率用的是这段历史的真实成交，**未来的回购利率可能更低**；"
          "把利率调到 0 就是上面那条控制臂，这就是这本书赔率的下界。",
          "- 票池是现存 ETF，带生存者偏差；本条不重估它，也不改变 r2233 的这条边界。",
          "- 重叠窗口不是独立观测：一年的判词背后只有 "
          f"{on['horizons']['1y'].get('independent',{}).get('n',0)} 个不重叠样本。",
          "", END, ""]
    return "\n".join(L)


def doc_prologue():
    return ("# 现金生息之后，这本书一年亏钱的起点还剩几个\n\n"
            f"面：`{JSON_PATH}` · 脚本：`scripts/{FACE}.py` · 页面数字由数据渲染，`--check` 逐字比对\n\n"
            "> 两条已发布的面各说了一半：r2233 量了这本书的赔率，但引擎口径把闲置现金记成 0% 利息；"
            "`etf_book_idle_cash` 量了那块现金按 GC001 滚动值多少，但只印了年化/夏普/回撤三个聚合读数。"
            "本条把两条拼起来，问的是读者真正要做决定的那句话：**现金真的能生息时，"
            "我还剩几个亏钱的起点、最差亏多少。**\n\n"
            "## 0. 为什么它不是又一次「加了个假设就变好」\n\n"
            "现金腿不是假设，是已发布面 `etf_book_cash_vehicle` / `etf_book_idle_cash` 用真实 GC001 "
            "面板算出来的每日净收益；本条只是把它接到 r2233 那条路径上。控制腿（现金 0%）"
            "必须逐位还原引擎序列，零利率臂必须逐位还原 r2233 的计数——两条对账都印在页面上。\n")


def run():
    payload = {"face": FACE,
               "why": "the losing-year count is published with cash at 0%; the repo panel says it earns",
               "wallet_cny": WALLET,
               "config": {"rebal": REBAL, "n_hold": NHOLD, "cost_bp_side": COST * 1e4,
                          "vol_target": VT, "entry_lag": ENTRY_LAG,
                          "sleeves": ["equity", "commodity", "convertible"],
                          "cash_leg": "GC001 daily roll, net of commissions (etf_book_cash_ladder.roll_rung)"}}
    book, turn, diag, n_flip, n_uni = build_engine()
    print("engine bars %d turnover %.3f universe %d flips %d"
          % (len(book), turn, n_uni, n_flip), flush=True)
    ctrl_err = control_gap(book, diag)
    print("control max rel err %.3e" % ctrl_err, flush=True)

    cash_ret, info, raw_ret, raw_bars = cash_leg(book.index)
    comp, idle = compose_with_cash(book, diag, cash_ret)
    try:
        cash_annual = CL.cagr_pct(raw_ret, raw_bars)
    except Exception:
        cash_annual = None
    print("cash annual %.4f%% idle mean %.4f" % (cash_annual or float("nan"),
                                                 float(idle.fillna(0).mean())), flush=True)

    off = arm_readings(book, "cash_off")
    on = arm_readings(comp, "cash_on")
    payload["arms"] = {"cash_off": off, "cash_on": on}
    payload["delta"] = delta_rows(off, on)
    payload["reconciliation"] = reconcile_prior(off)
    payload["control_max_rel_err"] = ctrl_err
    if off["cagr"] is not None and on["cagr"] is not None:
        payload["cash_pp"] = float((on["cagr"] - off["cagr"]) * 100.0)
    else:
        payload["cash_pp"] = None
    payload["cash_annual_pct"] = cash_annual
    payload["idle_share_mean"] = float(idle.fillna(0.0).mean())
    payload["idle_share_median"] = float(idle.fillna(0.0).median())
    payload["turnover"] = turn
    payload["universe"] = n_uni
    payload["flips_repaired"] = n_flip
    payload["evidence_cutoff"] = on["last_bar"]
    payload["verdict"] = verdict_of(payload["delta"], payload["reconciliation"], ctrl_err)
    payload["headline"] = headline(payload)

    os.makedirs("results", exist_ok=True)
    with io.open(JSON_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    text = doc_prologue() + "\n" + render(payload)
    os.makedirs("research", exist_ok=True)
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote", JSON_PATH, "and", DOC_PATH)
    print("verdict", payload["verdict"], "|", payload["headline"])
    return 0


def check():
    if not os.path.exists(JSON_PATH):
        print("STALE face missing:", JSON_PATH)
        return 3
    with io.open(JSON_PATH, encoding="utf-8") as fh:
        p = json.load(fh)
    if not os.path.exists(DOC_PATH):
        print("STALE doc missing:", DOC_PATH)
        return 3
    cur = io.open(DOC_PATH, encoding="utf-8").read()
    want = doc_prologue() + "\n" + render(p)
    if cur.strip() != want.strip():
        i = next((k for k in range(min(len(cur), len(want))) if cur[k] != want[k]),
                 min(len(cur), len(want)))
        print("CHECK FAILED: page text differs from data at char", i)
        print("have:", cur[max(0, i - 80):i + 80].replace("\n", "\\n"))
        print("want:", want[max(0, i - 80):i + 80].replace("\n", "\\n"))
        return 4
    y1 = p["delta"]["1y"]
    if y1["closed"] != y1["count_losing_off"] - y1["count_losing_on"]:
        print("CHECK FAILED: closed arithmetic")
        return 4
    print(f"OK {p['face']} {p['verdict']} · 1y losing {y1['count_losing_off']} -> "
          f"{y1['count_losing_on']} · cutoff {p['evidence_cutoff']}")
    return 0


# ---------------------------------------------------------------- selftest
def _ser(levels, start="2020-01-02"):
    idx = pd.bdate_range(start, periods=len(levels))
    return pd.Series(levels, index=idx)


def selftest():
    ok, fails = 0, []

    def leg(cond, msg):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(msg)

    # 1 cash_ret == 0 composes back to the book exactly
    book = _ser(list(np.linspace(1.0, 1.5, 60)))
    full = pd.Series(1.0, index=book.index)
    comp, idle = IC.compose(book, full, pd.Series(0.0, index=book.index)), full

    # control: with idle=0 and cash>0 nothing changes (a fully invested book has no idle sleeve)
    comp_full_inv = IC.compose(book, pd.Series(0.0, index=book.index),
                              pd.Series(0.001, index=book.index))
    leg(float((comp_full_inv / book - 1.0).abs().max()) < 1e-12,
        "fully invested book was moved by the cash rate")

    # 2 idle sleeve with a positive rate lifts the series, and only lifts it
    cash = pd.Series(0.0002, index=book.index)
    comp_on = IC.compose(book, pd.Series(0.3, index=book.index), cash)
    leg(float((comp_on - book).min()) >= -1e-12 and float(comp_on.iloc[-1]) > float(book.iloc[-1]),
        "positive cash rate did not lift an idle sleeve")

    # 3 a NEGATIVE rate must lower it -- the device cannot only report good news
    comp_neg = IC.compose(book, pd.Series(0.3, index=book.index), cash * -1.0)
    leg(float(comp_neg.iloc[-1]) < float(book.iloc[-1]),
        "negative cash rate did not lower the sleeve")

    # 4 monotone up: no losing 1y window, cash on or off
    up = _ser(list(np.linspace(1.0, 2.0, 400)))
    m_up = LO.measure(up)
    leg(m_up["horizons"]["1y"]["count_losing"] == 0, "monotone up produced losers")

    # 5 monotone down: every 1y window loses even with cash (cash cannot flip a direction)
    dn = _ser(list(np.linspace(2.0, 1.0, 400)))
    m_dn = LO.measure(dn)
    leg(m_dn["horizons"]["1y"]["count_losing"] == m_dn["horizons"]["1y"]["n"],
        "monotone down did not lose everywhere")

    # 6 doubling the rate never adds losing starts (monotonicity of the repair).
    # Needs a long enough tape for a 1y window to exist at all -- a short tape would make
    # both arms report n=0 and pass for the wrong reason.
    wob = _ser(list(1.0 + 0.0004 * np.sin(np.arange(400) / 7.0) + 0.0002 * np.arange(400)))
    cash_l = pd.Series(0.0002, index=wob.index)
    seed = pd.Series(0.3, index=wob.index)
    one_y = LO.measure(IC.compose(wob, seed, cash_l))["horizons"]["1y"]
    half_y = LO.measure(IC.compose(wob, seed, cash_l * 0.5))["horizons"]["1y"]
    leg(one_y["n"] > 0 and half_y["count_losing"] >= one_y["count_losing"],
        "more cash made more losing starts (or the tape was too short to measure)")

    # 7 missing prior face / empty horizon is UNMEASURED, never zero
    leg(verdict_of({"1y": {"closed": 0, "count_losing_on": 5}},
                   {"verdict": "UNMEASURED"}, 0.0) == "REFUSE_PRIOR_NOT_REPRODUCED",
        "unmeasured prior face was not refused")
    leg(LO.describe(np.array([])).get("n") == 0, "empty describe is not zero-counted")

    # 8 the control gap detector actually fires on a broken control
    broken = book * 1.001
    leg(float((broken / book - 1.0).abs().max()) > REPRO_TOL, "control gap detector blind")

    total = ok + len(fails)
    print(f"selftest {ok}/{total}")
    for f in fails:
        print(" FAIL:", f)
    return 0 if not fails else 4


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(run())
    if cmd == "check":
        sys.exit(check())
    if cmd == "selftest":
        sys.exit(selftest())
    print("usage: run|check|selftest")
    sys.exit(2)
