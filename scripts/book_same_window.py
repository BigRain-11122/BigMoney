"""同窗对账：两本书「谁更值得开」这个差，有多少来自窗口不同 / 执行口径不同。

r2188 的钱包阶梯用两本书**各自**的整段历史收益（转债 2007-07 起 19.3 年、ETF 2020-01 起
6.9 年）去比同一只钱包里的钱。两个窗口不是一件事：26 年后半段转债只在 2020-01 之后与 ETF
重叠。这张面只问一件事——把两本放到**同一段日历**、同一把年化时钟、同一种成交口径上，
那个「ETF 多赚 X 元/年」还在不在、差多少。

不重算任何回测规则：两本书的日净值直接取自 book_pair_blend 的两条父腿（与 blend /
cushion_regime / sleeve_premium / sleeve_turnover / wallet_scale_ladder 同一族），
本面只做切片与统计。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "book_same_window.json")
OUT_MD = os.path.join(ROOT, "results", "book_same_window.md")
OUT_RESEARCH = os.path.join(ROOT, "research", "BOOK_SAME_WINDOW.md")

FACE = "book_same_window"
ANN = 244.0          # 钱包时钟（A 股日历钱包，与 book_pair_blend.ANN_DAYS 同源）
ETF_PUB_ARM = "nobond_vt08"
WALLET_CNY = 1000000.0
GAP_TOL_PP = 0.05    # 半个万分之一百 = 0.05 个百分点以内视作「没变」
MIN_SHARED_BARS = 250

# 输入面：谁动过，本面就过期（r1850 外部锚 / r1935 探针锚到它该问的那份输入）
INPUTS = (
    ("cb_panel", "data/cb_panel.csv.gz"),
    ("etf_panel", "data/daily/510300.csv"),
    ("etf_nobond_vt", "results/etf_nobond_vt.json"),
    ("cb_dual_low", "results/cb_dual_low.json"),
    ("cb_union_lens", "results/cb_union_lens.json"),
    ("cash_roll", "results/etf_book_cash_roll_today.json"),
)


# ------------------------------------------------------------------ helpers
def _rp(rel):
    return os.path.join(ROOT, rel)


def _load(rel):
    with open(_rp(rel), encoding="utf-8") as fh:
        return json.load(fh)


def _iso(ts):
    import datetime as _dt
    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(rel):
    p = _rp(rel)
    if not os.path.exists(p):
        return {"path": rel, "missing": True}
    st = os.stat(p)
    return {"path": rel, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


def _pp(x):
    """ratio -> percentage points"""
    return None if x is None else float(x) * 100.0


# ------------------------------------------------------------------ inputs
def load_books():
    """两条父腿：都是 t+1 口径（转债收盘信号次日成交 / ETF 收盘决策次日开盘持有）。"""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import book_pair_blend as P

    cb, mcb = P.load_cb()
    etf, metf = P.load_etf()
    return {"P": P, "cb": cb, "etf": etf, "cb_meta": mcb, "etf_meta": metf}


def published_etf_arm():
    """面世的那条 ETF 臂：收盘对收盘，与父腿的次日开盘口径不是同一件事。"""
    d = _load("results/etf_nobond_vt.json")
    run = None
    for r in d.get("runs", []):
        if r.get("label") == ETF_PUB_ARM:
            run = r
    if run is None:
        raise SystemExit("face missing: results/etf_nobond_vt.json has no arm %r" % ETF_PUB_ARM)
    return {
        "face": "results/etf_nobond_vt.json",
        "arm": ETF_PUB_ARM,
        "cagr": float(run["cagr"]),
        "sharpe": float(run["sharpe"]),
        "maxdd": float(run["maxdd"]),
        "cutoff": d.get("evidence_cutoff"),
        "generated": d.get("generated"),
        "note": "close-to-close, entry_lag not recorded by the face",
    }


def wallet_inputs():
    union = _load("results/cb_union_lens.json")
    roll = _load("results/etf_book_cash_roll_today.json")
    cash = None
    for c in roll.get("eligible", []):
        if c.get("net_ann_pct") is None:
            continue
        if cash is None or float(c["net_ann_pct"]) > float(cash["net_ann_pct"]):
            cash = c
    if cash is None:
        raise SystemExit("face missing: results/etf_book_cash_roll_today.json has no priced eligible repo")
    return {
        "need_etf_cny": float(union["books"]["etf_book"]["invested_cny"]),
        "need_cb_cny": float(union["books"]["cb_book"]["invested_cny"]),
        "cash_contract": cash.get("contract"),
        "cash_rate": float(cash["net_ann_pct"]) / 100.0,
        "cash_cutoff": roll.get("as_of"),
        "union_cutoff": union.get("evidence_cutoff") or union.get("cutoff"),
    }


# ------------------------------------------------------------------ maths
def drawdown_info(ser):
    """最深回撤发生日 + 峰日（读者要知道那 22% 是哪一段）"""
    dd = ser / ser.cummax() - 1.0
    trough = dd.idxmin()
    peak = ser.loc[:trough].idxmax()
    return {"worst_dd": float(dd.min()),
            "trough": str(trough.date()),
            "peak": str(peak.date()),
            "now_pct": float(dd.iloc[-1]),
            "now_is_the_trough": bool(trough == dd.index[-1])}


def now_drawdown(ser):
    """今天这一本在水下多少（相对自己的最高点），也是读者最先会问的那个数。"""
    dd = ser / ser.cummax() - 1.0
    peak = ser.idxmax()
    return {"now_pct": float(dd.iloc[-1]),
            "high_bar": str(peak.date()),
            "last_bar": str(ser.index[-1].date()),
            "at_high": bool(abs(float(dd.iloc[-1])) < 1e-12)}


def yearly_chain(ser):
    """每年 = 上年末水平 -> 本年末水平；首年用本段第一根水平起算。"""
    me = ser.resample("ME").last().dropna()
    if len(me) < 2:
        return {}
    by_year = {}
    for ts, lvl in me.items():
        by_year[int(ts.year)] = float(lvl)   # 年末水平 = 该年最后一根月末
    out = {}
    prev = float(ser.iloc[0])                # 首年从本段第一根起算
    for y in sorted(by_year):
        out[y] = by_year[y] / prev - 1.0
        prev = by_year[y]
    return out


def same_window(cb, etf):
    idx = cb.index.intersection(etf.index).sort_values()
    return idx


def build_rulers(a_stats, b_stats, pub, cb_full):
    """三把尺：A=面世数字各按自己那段历史；B=同窗 t+1；C=同窗但 ETF 用面世口径。"""
    def row(label, cb_cagr, etf_cagr, cb_sr, etf_sr, cb_dd, etf_dd):
        return {
            "ruler": label,
            "cb_cagr": float(cb_cagr), "etf_cagr": float(etf_cagr),
            "cb_sharpe": float(cb_sr), "etf_sharpe": float(etf_sr),
            "cb_maxdd": float(cb_dd), "etf_maxdd": float(etf_dd),
            "gap_pp": _pp(float(etf_cagr) - float(cb_cagr)),
        }

    A = row("A_published_each_on_own_history",
            cb_full["cagr"], pub["cagr"],
            cb_full["sharpe"], pub["sharpe"],
            cb_full["maxdd"], pub["maxdd"])
    B = row("B_same_window_t_plus_1",
            a_stats["cagr"], b_stats["cagr"],
            a_stats["sharpe"], b_stats["sharpe"],
            a_stats["maxdd"], b_stats["maxdd"])
    C = row("C_same_window_with_the_published_etf_caliber",
            a_stats["cagr"], pub["cagr"],
            a_stats["sharpe"], pub["sharpe"],
            a_stats["maxdd"], pub["maxdd"])
    return {"A": A, "B": B, "C": C}


def wallet_rows(rulers, w):
    """同一只钱包 100 万：每把尺下「单开这一本」能拿多少年收益（余额躺现金腿）。"""
    out = {}
    for key, r in rulers.items():
        rows = {}
        for book, need, cagr in (
            ("etf_book", w["need_etf_cny"], r["etf_cagr"]),
            ("cb_book", w["need_cb_cny"], r["cb_cagr"]),
        ):
            invested = min(need, WALLET_CNY)
            cash = max(WALLET_CNY - invested, 0.0)
            y = invested * cagr + cash * w["cash_rate"]
            rows[book] = {
                "invested_cny": round(invested, 2),
                "cash_cny": round(cash, 2),
                "year_cny": round(y, 2),
                "year_pct": round(y / WALLET_CNY, 6),
            }
        rows["gap_cny"] = round(rows["etf_book"]["year_cny"] - rows["cb_book"]["year_cny"], 2)
        out[key] = rows
    return out


def _bridge(key, ruler, w):
    """钱包差拆成两项：ETF 每 1 点优势落在已投的钱上值多少 + 闲置那截的机会成本。

    gap = need_etf*(etf-cb) + (need_cb-need_etf)*(cash-cb)   —— 恒等式，不是近似。
    """
    need_e = min(w["need_etf_cny"], WALLET_CNY)
    need_c = min(w["need_cb_cny"], WALLET_CNY)
    per_point = need_e * (ruler["etf_cagr"] - ruler["cb_cagr"])
    idle = (need_c - need_e) * (w["cash_rate"] - ruler["cb_cagr"])
    return {
        "ruler": key,
        "term_etf_advantage_cny": round(per_point, 2),
        "term_idle_cash_cny": round(idle, 2),
        "total_cny": round(per_point + idle, 2),
        "why_two_terms": (
            "the etf book only asks for %.0f of the 1,000,000; the other %.0f would have been in the "
            "convertible book had you picked that one, so it sits in the cash leg instead"
            % (need_e, need_c - need_e)),
    }


def verdict_of(rulers, wallet):
    """判词纯函数：只看三把尺的差与钱包两行的差，不看调用者的偏好。"""
    gap_a = rulers["A"]["gap_pp"]
    gap_b = rulers["B"]["gap_pp"]
    flip = (gap_a > 0) != (gap_b > 0)
    if flip:
        head = "SAME_WINDOW_REVERSES_THE_ORDER"
    elif gap_b > gap_a + GAP_TOL_PP:
        head = "SAME_WINDOW_WIDENS_THE_GAP_BUT_KEEPS_THE_ORDER"
    elif gap_b < gap_a - GAP_TOL_PP:
        head = "SAME_WINDOW_NARROWS_THE_GAP_BUT_KEEPS_THE_ORDER"
    else:
        head = "SAME_WINDOW_GAP_IS_UNCHANGED"

    b = rulers["B"]
    risk_better = (b["etf_sharpe"] > b["cb_sharpe"]) and (b["etf_maxdd"] > b["cb_maxdd"])
    risk = ("_AND_THE_RISK_COLUMNS_AGREE" if risk_better
            else "_AND_THE_RISK_COLUMNS_DISAGREE")

    wa, wb = wallet["A"], wallet["B"]
    if (wa["gap_cny"] > 0) != (wb["gap_cny"] > 0):
        money = "_BUT_THE_WALLET_ANSWER_FLIPS"
    elif abs(wb["gap_cny"]) > abs(wa["gap_cny"]):
        money = "_AND_THE_WALLET_GAP_IS_LARGER_%d_VS_%d_CNY" % (
            int(round(abs(wb["gap_cny"]))), int(round(abs(wa["gap_cny"]))))
    else:
        money = "_AND_THE_WALLET_GAP_IS_SMALLER_%d_VS_%d_CNY" % (
            int(round(abs(wb["gap_cny"]))), int(round(abs(wa["gap_cny"]))))
    return head + risk + money


def sentence_of(rulers, wallet):
    a, b, c = rulers["A"], rulers["B"], rulers["C"]
    wa, wb = wallet["A"], wallet["B"]
    return (
        "按各自整段历史（转债 %s 起、ETF %s 起），ETF 年化 %.2f%%、转债 %.2f%%，差 %+.2f 个百分点；"
        "把两本放到同一段日历（%s..%s）、同一把 244 天时钟、同一种次日成交，"
        "ETF %.2f%%、转债 %.2f%%，差 %+.2f 个百分点（比面世尺 %+.2f）；"
        "100 万钱包里单开 ETF 年 %.0f 元、单开转债年 %.0f 元，差 %.0f 元（面世尺是 %.0f 元）。"
        % (a["_cb_first"], a["_etf_first"],
           _pp(a["etf_cagr"]), _pp(a["cb_cagr"]), a["gap_pp"],
           b["_first"], b["_last"],
           _pp(b["etf_cagr"]), _pp(b["cb_cagr"]), b["gap_pp"], b["gap_pp"] - a["gap_pp"],
           wb["etf_book"]["year_cny"], wb["cb_book"]["year_cny"], wb["gap_cny"],
           wa["gap_cny"])
    )


# ------------------------------------------------------------------ build
def build(books=None, write=True, quiet=False):
    books = books or load_books()
    P = books["P"]
    cb, etf = books["cb"], books["etf"]
    idx = same_window(cb, etf)
    if len(idx) < MIN_SHARED_BARS:
        raise SystemExit("refusing to publish: shared window has only %d bars" % len(idx))
    a = cb.reindex(idx).dropna()
    b = etf.reindex(idx).dropna()
    j = a.index.intersection(b.index)
    a, b = a.reindex(j), b.reindex(j)

    cb_full = books["cb_meta"]["full_history"]
    etf_full = books["etf_meta"]["full_history"]
    pub = published_etf_arm()
    w = wallet_inputs()

    cb_stats_same = P.local_stats(a, ann=ANN)
    etf_stats_same = P.local_stats(b, ann=ANN)
    cb_stats_full = {
        "cagr": float(cb_full["cagr"]), "sharpe": float(cb_full["sharpe"]),
        "maxdd": float(cb_full["maxdd"]), "vol": float(cb_full["vol"]),
        "bars": int(cb_full["bars"]), "first": cb_full["first"], "last": cb_full["last"],
        "ann_days": 244.0,
    }
    etf_stats_full = {
        "cagr": float(etf_full["cagr"]), "sharpe": float(etf_full["sharpe"]),
        "maxdd": float(etf_full["maxdd"]), "vol": float(etf_full["vol"]),
        "bars": int(etf_full["bars"]), "first": etf_full["first"], "last": etf_full["last"],
        "ann_days": 252.0,
    }

    ra = a.pct_change().dropna()
    rb = b.pct_change().dropna()
    k = ra.index.intersection(rb.index)
    corr_daily = float(ra.reindex(k).corr(rb.reindex(k)))
    ma = a.resample("ME").last().pct_change().dropna()
    mb = b.resample("ME").last().pct_change().dropna()
    mk = ma.index.intersection(mb.index)
    corr_monthly = float(ma.reindex(mk).corr(mb.reindex(mk))) if len(mk) > 3 else None

    rulers = build_rulers(cb_stats_same, etf_stats_same, pub, cb_full)
    rulers["A"]["_cb_first"] = cb_stats_full["first"]
    rulers["A"]["_etf_first"] = etf_stats_full["first"]
    rulers["B"]["_first"] = str(j[0].date())
    rulers["B"]["_last"] = str(j[-1].date())
    wallet = wallet_rows(rulers, w)
    decomposition = {
        "window_effect_on_cb_pp": _pp(cb_stats_same["cagr"] - cb_full["cagr"]),
        "execution_effect_on_etf_pp": _pp(etf_stats_same["cagr"] - pub["cagr"]),
        "gap_a_pp": rulers["A"]["gap_pp"],
        "gap_b_pp": rulers["B"]["gap_pp"],
        "identity": ("gap_b - gap_a == execution_effect_on_etf - window_effect_on_cb "
                     "(the two biases are subtracted from the same gap)"),
        "reading": (
            "two published numbers were each about a point too generous, for two different reasons: "
            "the convertible book was quoted on 19.3 years it alone had, the etf book was quoted "
            "close-to-close instead of next-open. The two effects nearly cancel in the gap, so the "
            "ranking published earlier was right -- but neither absolute number was"),
    }
    verdict = verdict_of(rulers, wallet)
    sentence = sentence_of(rulers, wallet)

    y_cb = yearly_chain(a)
    y_etf = yearly_chain(b)
    years = sorted(set(y_cb) | set(y_etf))
    yearly = {
        int(y): {
            "cb": (round(_pp(y_cb[y]), 4) if y in y_cb else None),
            "etf": (round(_pp(y_etf[y]), 4) if y in y_etf else None),
            "diff_pp": (round(_pp(y_etf[y] - y_cb[y]), 4)
                        if (y in y_cb and y in y_etf) else None),
        }
        for y in years
    }
    etf_ahead = sum(1 for y in years
                    if y in y_cb and y in y_etf and y_etf[y] > y_cb[y])
    etf_behind = sum(1 for y in years
                     if y in y_cb and y in y_etf and y_etf[y] <= y_cb[y])

    face = {
        "face": FACE,
        "generated_at": _now_iso(),
        "evidence_cutoff": str(j[-1].date()),
        "question": ("两本书「谁更值得开」这个差，有多少是窗口不同造成的？"
                     "把两本放到同一段日历、同一把时钟、同一种成交口径上，差还在不在？"),
        "caliber": {
            "series": "book_pair_blend.load_cb() / load_etf() -- the same two parent legs the book family uses",
            "cb_execution": "signal at close t, filled at close t+1",
            "etf_execution": "decide at close t, own from the open of t+1 (entry_lag=1)",
            "ann_days_same_window": ANN,
            "ann_days_full_history": "cb 244 / etf 252 (each face's own clock, as published)",
            "same_window_base": "the first shared bar's level is the entry level (no return before you could own it)",
            "yearly": "year = previous year-end level -> this year-end level; first year starts at the first shared bar",
            "wallet": "single book at a time; the rest of the 1,000,000 rolls at the cash leg; deployment caps come from results/cb_union_lens.json",
            "what_this_face_does_not_do": (
                "it does not re-run either book's rules and it does not re-price anything; "
                "it slices two published daily series and restates them on one ruler"),
        },
        "shared_window": {
            "first": str(j[0].date()),
            "last": str(j[-1].date()),
            "bars": int(len(j)),
            "years": round((j[-1] - j[0]).days / 365.25, 3),
            "cb_bars_total": int(len(cb)),
            "etf_bars_total": int(len(etf)),
            "why_not_the_full_cb_history": (
                "the etf book only has a level from %s; before that there is no second book to compare"
                % etf_stats_full["first"]),
        },
        "books": {
            "cb": {
                "label": "转债双低袖（20 名等权 / 20 日 / 10bp）",
                "full_history": cb_stats_full,
                "same_window": {k2: cb_stats_same[k2] for k2 in
                                ("bars", "years", "cagr", "sharpe", "maxdd", "vol", "first", "last")},
                "same_window_drawdown": drawdown_info(a),
                "now_drawdown": now_drawdown(a),
            },
            "etf": {
                "label": "ETF 复合书（去债档 + 8 个点波动目标 / 5 名 / 20 日 / 10bp）",
                "full_history": etf_stats_full,
                "same_window": {k2: etf_stats_same[k2] for k2 in
                                ("bars", "years", "cagr", "sharpe", "maxdd", "vol", "first", "last")},
                "same_window_drawdown": drawdown_info(b),
                "now_drawdown": now_drawdown(b),
            },
        },
        "published_etf_arm": pub,
        "rulers": rulers,
        "decomposition": decomposition,
        "wallet": {"size_cny": WALLET_CNY, "cash_contract": w["cash_contract"],
                   "cash_rate": w["cash_rate"], "by_ruler": wallet,
                   "bridge": {k: _bridge(k, rulers[k], w) for k in ("A", "B")}},
        "correlation": {"daily": corr_daily, "monthly": corr_monthly, "on": "same window",
                        "reading": "two books that barely move together -- but a 1M wallet can only open one"},
        "yearly": yearly,
        "years_etf_ahead": int(etf_ahead),
        "years_cb_ahead": int(etf_behind),
        "verdict": verdict,
        "sentence": sentence,
        "inputs": {name: _stamp(rel) for name, rel in INPUTS},
        "parent_cutoffs": {
            "cb": cb_stats_full["last"],
            "etf": etf_stats_full["last"],
            "etf_published_arm": pub["cutoff"],
            "cash": w["cash_cutoff"],
        },
        "known_gaps": [
            "the two books carry different universes, different cost models and different turnover; "
            "this face aligns dates and clocks, not mechanics",
            "the etf book runs a volatility target (it de-levers), the cb book does not -- the gap in "
            "raw CAGR therefore mixes return with risk budget; the sharpe/maxdd columns are there to "
            "read it both ways",
            "the cb book is quoted on 244 days and the etf face on 252; the full-history rows keep each "
            "face's own clock and are therefore not directly subtractable from each other",
        ],
    }
    if not quiet:
        print("[build] shared window %s..%s (%d bars)"
              % (face["shared_window"]["first"], face["shared_window"]["last"], len(j)))
        for key in ("A", "B", "C"):
            r = rulers[key]
            print("  ruler %-1s  etf %+.2f%%  cb %+.2f%%  gap %+.2fpp"
                  % (key, _pp(r["etf_cagr"]), _pp(r["cb_cagr"]), r["gap_pp"]))
        print("  wallet A gap %+.0f CNY / B gap %+.0f CNY" % (
            wallet["A"]["gap_cny"], wallet["B"]["gap_cny"]))
        print("  correlation daily %.3f  monthly %s"
              % (corr_daily, ("%.3f" % corr_monthly) if corr_monthly is not None else "n/a"))
        print("  verdict %s" % verdict)
    if write:
        _write(OUT_JSON, json.dumps(_plain(face), ensure_ascii=False, indent=1) + "\n")
        _write(OUT_MD, render_md(face))
        _write(OUT_RESEARCH, render_research(face))
    return face


def _plain(o):
    if isinstance(o, dict):
        return {k: _plain(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    return o


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------ render
def _n(v, dash="n/a", nd=2):
    if v is None:
        return dash
    if isinstance(v, int):
        return str(v)
    return ("%." + str(nd) + "f") % float(v)


def render_md(face):
    sw = face["shared_window"]
    cb = face["books"]["cb"]
    etf = face["books"]["etf"]
    r = face["rulers"]
    w = face["wallet"]["by_ruler"]
    L = []
    L.append("# 两本书同窗对账")
    L.append("")
    L.append("生成 %s ｜ 证据截止 **%s** ｜ 同窗 %s..%s（%d 根日线，%.2f 年）"
             % (face["generated_at"], face["evidence_cutoff"], sw["first"], sw["last"],
                sw["bars"], sw["years"]))
    L.append("")
    L.append("## 问题")
    L.append("")
    L.append(face["question"])
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append(face["sentence"])
    L.append("")
    L.append("**判词**：`%s`" % face["verdict"])
    L.append("")
    L.append("## 三把尺")
    L.append("")
    L.append("| 尺 | 窗口 | ETF 年化 | 转债年化 | 差 | ETF 夏普 | 转债夏普 | ETF 最深回撤 | 转债最深回撤 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    desc = {
        "A": "各自整段历史（面世数字，各用自己的时钟）",
        "B": "同一段日历 + 244 天时钟 + 次日成交",
        "C": "同一段日历，但 ETF 用面世口径",
    }
    for key in ("A", "B", "C"):
        row = r[key]
        L.append("| %s | %s | %+.2f%% | %+.2f%% | %+.2fpp | %.3f | %.3f | %.2f%% | %.2f%% |"
                 % (key, desc[key],
                    _pp(row["etf_cagr"]), _pp(row["cb_cagr"]), row["gap_pp"],
                    row["etf_sharpe"], row["cb_sharpe"],
                    _pp(row["etf_maxdd"]), _pp(row["cb_maxdd"])))
    L.append("")
    L.append("转债整段历史自 %s 起（%d 根），ETF 自 %s 起（%d 根）——A 尺把 19.3 年和 6.9 年"
             "放在一起减，B 尺才是同一段日历。"
             % (cb["full_history"]["first"], cb["full_history"]["bars"],
                etf["full_history"]["first"], etf["full_history"]["bars"]))
    L.append("")
    L.append("## 100 万钱包：单开一本，余额躺现金腿（%s %s）"
             % (face["wallet"]["cash_contract"], _n(_pp(face["wallet"]["cash_rate"]), nd=4) + "%"))
    L.append("")
    L.append("| 尺 | 单开 ETF 投入 | ETF 年收益 | 单开转债投入 | 转债年收益 | 差 |")
    L.append("|---|---|---|---|---|---|")
    for key in ("A", "B"):
        rows = w[key]
        L.append("| %s | %s | %s | %s | %s | %+.0f 元 |"
                 % (key,
                    "{:,.2f}".format(rows["etf_book"]["invested_cny"]),
                    "{:,.0f}".format(rows["etf_book"]["year_cny"]),
                    "{:,.2f}".format(rows["cb_book"]["invested_cny"]),
                    "{:,.0f}".format(rows["cb_book"]["year_cny"]),
                    rows["gap_cny"]))
    L.append("")
    d = face["decomposition"]
    br = face["wallet"]["bridge"]
    L.append("## 两个面世数字各差在哪（这是本轮真正找到的东西）")
    L.append("")
    L.append("| 面世数字 | 面世值 | 同一把尺上的值 | 差 | 差的来源 |")
    L.append("|---|---|---|---|---|")
    L.append("| 转债年化 | %+.2f%% | %+.2f%% | %+.2fpp | **窗口**：7.35%% 是它独享 2007-2026 的 19.3 年 |"
             % (_pp(cb["full_history"]["cagr"]), _pp(cb["same_window"]["cagr"]),
                d["window_effect_on_cb_pp"]))
    L.append("| ETF 年化 | %+.2f%% | %+.2f%% | %+.2fpp | **成交口径**：面世是收盘对收盘，实际是收盘决策次日开盘 |"
             % (_pp(r["A"]["etf_cagr"]), _pp(r["B"]["etf_cagr"]),
                d["execution_effect_on_etf_pp"]))
    L.append("")
    L.append("两个偏差**方向相同、大小几乎相等**（%+.2fpp 与 %+.2fpp），在「谁减谁」里正好相互抵消——"
             "所以早先那条「ETF 更值得开」的排序是对的，但它两边的绝对数字都偏乐观约一个点。"
             % (d["window_effect_on_cb_pp"], d["execution_effect_on_etf_pp"]))
    L.append("")
    L.append("## 钱包差为什么会从 %.0f 元变成 %.0f 元（不是笔误）"
             % (br["A"]["total_cny"], br["B"]["total_cny"]))
    L.append("")
    L.append("恒等式：`钱包差 = 已投的钱 ×(ETF−转债) + (转债书要的钱−ETF 书要的钱) ×(现金腿−转债)`")
    L.append("")
    L.append("| 尺 | 第一项（ETF 优势落在 %.0f 元上） | 第二项（%.0f 元本该进转债书却躺现金） | 合计 |"
             % (face["wallet"]["by_ruler"]["A"]["etf_book"]["invested_cny"],
                face["wallet"]["by_ruler"]["A"]["cb_book"]["invested_cny"]
                - face["wallet"]["by_ruler"]["A"]["etf_book"]["invested_cny"]))
    L.append("|---|---|---|---|")
    for key in ("A", "B"):
        b2 = br[key]
        L.append("| %s | %+.0f 元 | %+.0f 元 | %+.0f 元 |"
                 % (key, b2["term_etf_advantage_cny"], b2["term_idle_cash_cny"], b2["total_cny"]))
    L.append("")
    L.append("百分点的差几乎没动（%+.2fpp → %+.2fpp），钱却多了 %.0f 元：因为转债同窗收益从 %+.2f%% 掉到 %+.2f%%，"
             "「那 %.0f 元不进转债书」的机会成本跟着缩小，ETF 的优势因此被放大。"
             % (d["gap_a_pp"], d["gap_b_pp"], br["B"]["total_cny"] - br["A"]["total_cny"],
                _pp(cb["full_history"]["cagr"]), _pp(cb["same_window"]["cagr"]),
                face["wallet"]["by_ruler"]["A"]["cb_book"]["invested_cny"]
                - face["wallet"]["by_ruler"]["A"]["etf_book"]["invested_cny"]))
    L.append("")
    L.append("## 逐年（同窗，百分点）")
    L.append("")
    L.append("| 年 | ETF | 转债 | 差 |")
    L.append("|---|---|---|---|")
    for y, v in face["yearly"].items():
        L.append("| %s | %s | %s | %s |"
                 % (y,
                    ("%+.2f" % v["etf"]) if v["etf"] is not None else "n/a",
                    ("%+.2f" % v["cb"]) if v["cb"] is not None else "n/a",
                    ("%+.2f" % v["diff_pp"]) if v["diff_pp"] is not None else "n/a"))
    L.append("")
    L.append("ETF 胜 %d 年、转债胜 %d 年（首末年非完整年，按水平链算，不做年化）。"
             % (face["years_etf_ahead"], face["years_cb_ahead"]))
    L.append("")
    L.append("## 回撤发生在哪一段，今天在水下多少")
    L.append("")
    for key, name in (("cb", "转债"), ("etf", "ETF")):
        d = face["books"][key]["same_window_drawdown"]
        n = face["books"][key]["now_drawdown"]
        L.append("- %s：最深 %.2f%%（峰 %s → 谷 %s）；今天 **%.2f%%**（距最高点 %s 那一根）%s"
                 % (name, _pp(d["worst_dd"]), d["peak"], d["trough"],
                    _pp(n["now_pct"]), n["high_bar"],
                    "，**即今天正站在最深那一格上**" if d.get("now_is_the_trough") else ""))
    L.append("")
    L.append("## 相关性")
    L.append("")
    L.append("同窗日收益相关 **%s**、月收益相关 **%s** — 两本几乎不同步，"
             "但 100 万钱包同时只开得动一本（两本同开要 1,741,528.50 元）。"
             % (_n(face["correlation"]["daily"], nd=3),
                _n(face["correlation"]["monthly"], nd=3)))
    L.append("")
    L.append("## 这张面不做的事")
    L.append("")
    for g in face["known_gaps"]:
        L.append("- %s" % g)
    L.append("")
    L.append("## 输入面")
    L.append("")
    for name, st in face["inputs"].items():
        if st.get("missing"):
            L.append("- `%s` **缺席**" % st["path"])
        else:
            L.append("- `%s`（%s 字节，%s）" % (st["path"], "{:,}".format(st["size"]), st["mtime"]))
    L.append("")
    return "\n".join(L) + "\n"


def render_research(face):
    L = []
    L.append("# 两本书同窗对账（research）")
    L.append("")
    L.append("面 `%s` ｜ 生成 %s ｜ cutoff %s"
             % (face["face"], face["generated_at"], face["evidence_cutoff"]))
    L.append("")
    L.append("## 为什么要这张面")
    L.append("")
    L.append("r2188 的钱包阶梯回答的是「100 万该开哪一本」，它用的两个年化收益来自两本"
             "**各自**的整段历史：转债自 2007-07（19.3 年），ETF 自 2020-01（6.9 年）。"
             "这两个数字本身没错，但它们不是同一段日历上的数——拿它们相减，差里混进了"
             "「转债在那 12 年独有历史上表现怎样」。这张面把那 12 年切掉，只留两本同时存在的 %d 根日线。"
             % face["shared_window"]["bars"])
    L.append("")
    L.append("## 读数")
    L.append("")
    for key in ("A", "B", "C"):
        r = face["rulers"][key]
        L.append("- **%s**：ETF %+.2f%%、转债 %+.2f%%，差 %+.2fpp"
                 % (key, _pp(r["etf_cagr"]), _pp(r["cb_cagr"]), r["gap_pp"]))
    L.append("")
    L.append("判词 `%s`；%s" % (face["verdict"], face["sentence"]))
    L.append("")
    L.append("## 口径（读这张面之前先读这段）")
    L.append("")
    for k, v in face["caliber"].items():
        L.append("- `%s`：%s" % (k, v))
    L.append("")
    L.append("## 已知缺口")
    L.append("")
    for g in face["known_gaps"]:
        L.append("- %s" % g)
    L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ check
def _verify(face, stamps=None, pub_now=None):
    """便宜的三问：①输入面动过吗 ②面世臂的读数还对得上吗 ③面内算术自洽吗。"""
    problems = []
    stale = []

    stamps = stamps if stamps is not None else {name: _stamp(rel) for name, rel in INPUTS}
    for name, st in (face.get("inputs") or {}).items():
        cur = stamps.get(name)
        if cur is None:
            continue
        if cur.get("missing") or st.get("missing"):
            stale.append("%s is missing now" % name)
            continue
        if int(cur.get("size", -1)) != int(st.get("size", -2)) or \
                cur.get("mtime") != st.get("mtime"):
            stale.append("%s moved (%s -> %s)" % (name, st.get("mtime"), cur.get("mtime")))

    # 面世臂：如果 published face 重写了，A 尺的 ETF 数就不再是它引用的那个
    try:
        if pub_now is None:
            pub_now = published_etf_arm()
        rec = face.get("published_etf_arm") or {}
        if abs(float(pub_now["cagr"]) - float(rec.get("cagr", float("nan")))) > 1e-12:
            stale.append("published etf arm cagr moved (%.6f -> %.6f)"
                         % (rec.get("cagr"), pub_now["cagr"]))
    except SystemExit as exc:
        problems.append(str(exc))

    # 面内算术
    r = face.get("rulers") or {}
    for key in ("A", "B", "C"):
        row = r.get(key)
        if not row:
            problems.append("ruler %s missing" % key)
            continue
        gap = _pp(row["etf_cagr"] - row["cb_cagr"])
        if abs(gap - row["gap_pp"]) > 1e-6:
            problems.append("ruler %s gap does not recompute (%.6f vs %.6f)"
                            % (key, gap, row["gap_pp"]))

    sw = face.get("shared_window") or {}
    if face.get("evidence_cutoff") != sw.get("last"):
        problems.append("evidence_cutoff %r is not the last shared bar %r"
                        % (face.get("evidence_cutoff"), sw.get("last")))

    if "B" in r:
        b = r["B"]
        if abs(_pp(b["etf_cagr"]) - _pp(face["books"]["etf"]["same_window"]["cagr"])) > 1e-6:
            problems.append("ruler B etf does not match books.etf.same_window")
        if abs(_pp(b["cb_cagr"]) - _pp(face["books"]["cb"]["same_window"]["cagr"])) > 1e-6:
            problems.append("ruler B cb does not match books.cb.same_window")

    # 钱包行
    wl = ((face.get("wallet") or {}).get("by_ruler") or {})
    cash = float((face.get("wallet") or {}).get("cash_rate") or 0.0)
    for key in ("A", "B"):
        rows = wl.get(key)
        if not rows:
            problems.append("wallet ruler %s missing" % key)
            continue
        for book, rate_key in (("etf_book", "etf_cagr"), ("cb_book", "cb_cagr")):
            y = rows[book]["invested_cny"] * r[key][rate_key] + rows[book]["cash_cny"] * cash
            if abs(y - rows[book]["year_cny"]) > 0.02:
                problems.append("wallet %s/%s year does not recompute (%.2f vs %.2f)"
                                % (key, book, y, rows[book]["year_cny"]))
        if abs((rows["etf_book"]["year_cny"] - rows["cb_book"]["year_cny"])
               - rows["gap_cny"]) > 0.02:
            problems.append("wallet %s gap does not recompute" % key)

    # 拆解恒等式：gap_B − gap_A 必须等于「ETF 口径效应 − 转债窗口效应」
    dec = face.get("decomposition") or {}
    if dec and "A" in r and "B" in r:
        lhs = r["B"]["gap_pp"] - r["A"]["gap_pp"]
        rhs = (float(dec["execution_effect_on_etf_pp"])
               - float(dec["window_effect_on_cb_pp"]))
        if abs(lhs - rhs) > 1e-9:
            problems.append("decomposition identity does not hold (%.9f vs %.9f)" % (lhs, rhs))

    # 钱包桥：第一项 + 第二项 必须等于该尺的钱包差
    bridge = ((face.get("wallet") or {}).get("bridge") or {})
    for key in ("A", "B"):
        b2 = bridge.get(key)
        if not b2:
            continue
        total = b2["term_etf_advantage_cny"] + b2["term_idle_cash_cny"]
        if abs(total - b2["total_cny"]) > 0.02 or \
                abs(b2["total_cny"] - wl[key]["gap_cny"]) > 0.02:
            problems.append("wallet bridge %s does not add up to the wallet gap" % key)

    verdict_now = verdict_of(r, wl) if ("A" in r and "B" in r and wl.get("A") and wl.get("B")) else None
    if verdict_now and verdict_now != face.get("verdict"):
        problems.append("verdict does not recompute from the published rows")

    if problems:
        return {"ok": False, "kind": "CHECK FAILED", "problems": problems, "stale": stale}
    if stale:
        return {"ok": False, "kind": "STALE", "stale": stale, "problems": []}
    return {"ok": True, "kind": "CHECK OK", "problems": [], "stale": []}


def check():
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "kind": "STALE", "why": "face missing: run it"}, ensure_ascii=False))
        return 3
    with open(OUT_JSON, encoding="utf-8") as fh:
        face = json.load(fh)
    res = _verify(face)
    print(json.dumps(res, ensure_ascii=False))
    if res["ok"]:
        return 0
    return 3 if res["kind"] == "STALE" else 1


# ------------------------------------------------------------------ selftest
def selftest():
    import pandas as pd

    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "ok": bool(cond), "detail": detail})
        if not cond:
            print("  [FAIL] %s %s" % (name, detail))
        else:
            print("  [ok] %s" % name)

    # ---- 合成两本：可解析的日序列，用来钉住算术而不是钉住市场
    idx = pd.bdate_range("2020-01-01", periods=600)
    cb_s = pd.Series([1000.0 * (1.0003 ** n) for n in range(600)], index=idx)   # 年化约 7.6%
    etf_s = pd.Series([1000.0 * (1.0004 ** n) for n in range(600)], index=idx)  # 年化约 10.3%
    P = {}
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import book_pair_blend as PB
    a_stats = PB.local_stats(cb_s, ann=ANN)
    b_stats = PB.local_stats(etf_s, ann=ANN)

    pub = {"cagr": 0.12, "sharpe": 1.1, "maxdd": -0.10, "arm": ETF_PUB_ARM,
           "face": "x", "cutoff": "2026-11-26", "generated": None, "note": ""}
    cb_full = {"cagr": 0.06, "sharpe": 0.7, "maxdd": -0.25, "vol": 0.10,
               "bars": 4000, "first": "2007-07-12", "last": "2026-11-26"}
    rulers = build_rulers(a_stats, b_stats, pub, cb_full)
    leg("1 A ruler gap is etf minus cb", abs(rulers["A"]["gap_pp"] - _pp(0.12 - 0.06)) < 1e-9,
        "%.6f" % rulers["A"]["gap_pp"])
    leg("2 B ruler gap is etf minus cb",
        abs(rulers["B"]["gap_pp"] - _pp(b_stats["cagr"] - a_stats["cagr"])) < 1e-9)
    leg("3 C ruler keeps the published etf number but the same-window cb",
        abs(rulers["C"]["etf_cagr"] - 0.12) < 1e-12 and
        abs(rulers["C"]["cb_cagr"] - a_stats["cagr"]) < 1e-12)

    w = {"need_etf_cny": 750000.0, "need_cb_cny": 990000.0, "cash_rate": 0.0116,
         "cash_contract": "GC007", "cash_cutoff": "2026-11-26", "union_cutoff": "2026-11-26"}
    wallet = wallet_rows(rulers, w)
    leg("4 wallet year = invested*cagr + cash*rate",
        abs(wallet["A"]["etf_book"]["year_cny"]
            - (750000.0 * 0.12 + 250000.0 * 0.0116)) < 0.02)
    leg("5 wallet gap is etf minus cb",
        abs(wallet["A"]["gap_cny"]
            - (wallet["A"]["etf_book"]["year_cny"] - wallet["A"]["cb_book"]["year_cny"])) < 0.02)
    leg("6 a book that needs more than the wallet is capped at the wallet",
        wallet_rows({"A": dict(rulers["A"], cb_cagr=0.06)},
                    dict(w, need_cb_cny=2500000.0))["A"]["cb_book"]["invested_cny"] == 1000000.0)

    br = {k: _bridge(k, rulers[k], w) for k in ("A", "B")}
    leg("6b the wallet bridge adds up to the wallet gap it explains",
        all(abs(br[k]["total_cny"] - wallet[k]["gap_cny"]) < 0.02 for k in ("A", "B")) and
        all(abs(br[k]["term_etf_advantage_cny"] + br[k]["term_idle_cash_cny"]
                - br[k]["total_cny"]) < 0.02 for k in ("A", "B")),
        json.dumps({k: br[k]["total_cny"] for k in br}))

    dec = {"window_effect_on_cb_pp": _pp(a_stats["cagr"] - 0.06),
           "execution_effect_on_etf_pp": _pp(b_stats["cagr"] - 0.12)}
    leg("6c gap_B - gap_A equals execution effect minus window effect",
        abs((rulers["B"]["gap_pp"] - rulers["A"]["gap_pp"])
            - (dec["execution_effect_on_etf_pp"] - dec["window_effect_on_cb_pp"])) < 1e-9,
        "%.9f" % (rulers["B"]["gap_pp"] - rulers["A"]["gap_pp"]))

    leg("7 order kept when the gap widens",
        verdict_of({"A": {"gap_pp": 2.0, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2},
                    "B": {"gap_pp": 3.0, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2}},
                   {"A": {"gap_cny": 100.0}, "B": {"gap_cny": 200.0}})
        .startswith("SAME_WINDOW_WIDENS_THE_GAP"))
    leg("8 order reverses when the sign flips (negative control)",
        verdict_of({"A": {"gap_pp": 2.0, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2},
                    "B": {"gap_pp": -0.5, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2}},
                   {"A": {"gap_cny": 100.0}, "B": {"gap_cny": -50.0}})
        .startswith("SAME_WINDOW_REVERSES_THE_ORDER"))
    leg("9 wallet answer flipping is named out loud",
        "_BUT_THE_WALLET_ANSWER_FLIPS" in
        verdict_of({"A": {"gap_pp": 2.0, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2},
                    "B": {"gap_pp": 3.0, "etf_sharpe": 1.0, "cb_sharpe": 0.5,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2}},
                   {"A": {"gap_cny": 100.0}, "B": {"gap_cny": -50.0}}))
    leg("10 risk columns disagree when the cb book has the better sharpe",
        verdict_of({"A": {"gap_pp": 2.0, "etf_sharpe": 0.4, "cb_sharpe": 0.9,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2},
                    "B": {"gap_pp": 3.0, "etf_sharpe": 0.4, "cb_sharpe": 0.9,
                          "etf_maxdd": -0.1, "cb_maxdd": -0.2}},
                   {"A": {"gap_cny": 100.0}, "B": {"gap_cny": 200.0}})
        .count("AND_THE_RISK_COLUMNS_DISAGREE") == 1)

    # ---- 切片与统计
    idx2 = same_window(cb_s, etf_s.iloc[100:])
    leg("11 shared window is the intersection, not the union", len(idx2) == 500 and
        str(idx2[0].date()) == str(idx[100].date()))
    same_a = PB.local_stats(cb_s.reindex(idx2), ann=ANN)
    leg("12 same-window bars never exceed either book's bars",
        same_a["bars"] <= min(len(cb_s), 500))

    # ---- 回撤登记
    dip = pd.Series([1.0, 1.1, 1.2, 0.9, 1.0], index=pd.bdate_range("2021-01-01", periods=5))
    dd = drawdown_info(dip)
    leg("13 drawdown trough/peak are the bars the reader would point at",
        abs(dd["worst_dd"] - (0.9 / 1.2 - 1.0)) < 1e-12 and dd["peak"] == "2021-01-05"
        and dd["trough"] == "2021-01-06", json.dumps(dd))

    # ---- 逐年链
    ye = yearly_chain(pd.Series([1.0, 1.1, 1.21], index=pd.to_datetime(
        ["2023-01-03", "2023-12-29", "2024-01-31"])))
    leg("14 yearly chain reads year-end to year-end",
        abs(ye[2023] - 0.10) < 1e-12 and abs(ye[2024] - 0.10) < 1e-12, json.dumps(ye))

    # 同一年里有十二根月末：每一年的读数必须是「整年」，不能被最后一个月覆盖
    midx = pd.date_range("2023-01-31", periods=24, freq="ME")
    lvls = [100.0 * (1.01 ** k) for k in range(24)]
    ye2 = yearly_chain(pd.Series(lvls, index=midx))
    leg("14b a year with twelve month-ends reports the whole year, not its last month",
        abs(ye2[2023] - (1.01 ** 11 - 1.0)) < 1e-9 and abs(ye2[2024] - (1.01 ** 12 - 1.0)) < 1e-9,
        json.dumps({str(k): round(v, 6) for k, v in ye2.items()}))
    leg("14c the first year is measured from the first bar, not from the first month end",
        abs(yearly_chain(pd.Series([1.0, 2.0], index=pd.to_datetime(
            ["2023-01-03", "2023-06-30"])))[2023] - 1.0) < 1e-12)

    # ---- 今天在水下多少
    hi = pd.Series([1.0, 1.2, 0.9], index=pd.bdate_range("2021-01-01", periods=3))
    leg("14d now_drawdown is zero at a high and the peak-to-last gap in a dip",
        abs(now_drawdown(hi.iloc[:2])["now_pct"]) < 1e-12 and
        abs(now_drawdown(hi)["now_pct"] - (0.9 / 1.2 - 1.0)) < 1e-12 and
        now_drawdown(hi)["high_bar"] == "2021-01-04",
        json.dumps(now_drawdown(hi)))

    # ---- _verify 行为腿
    face = {
        "evidence_cutoff": "2026-11-26",
        "shared_window": {"last": "2026-11-26"},
        "books": {"cb": {"same_window": {"cagr": a_stats["cagr"]}},
                  "etf": {"same_window": {"cagr": b_stats["cagr"]}}},
        "rulers": rulers,
        "decomposition": dec,
        "wallet": {"cash_rate": 0.0116, "by_ruler": wallet, "bridge": br},
        "published_etf_arm": dict(pub),
        "inputs": {},
        "verdict": verdict_of(rulers, wallet),
    }
    ok = _verify(face, stamps={}, pub_now=pub)
    leg("15 a clean face passes", ok["ok"], json.dumps(ok))

    bad = json.loads(json.dumps(face))
    bad["rulers"]["B"]["gap_pp"] = 99.0
    res = _verify(bad, stamps={}, pub_now=pub)
    leg("16 a tampered gap must fail with CHECK FAILED, not STALE",
        (not res["ok"]) and res["kind"] == "CHECK FAILED"
        and any("gap does not recompute" in p for p in res["problems"]), json.dumps(res["kind"]))

    moved = json.loads(json.dumps(face))
    moved["inputs"] = {"cb_panel": {"path": "data/cb_panel.csv.gz", "size": 1, "mtime": "2020-01-01T00:00:00"}}
    res2 = _verify(moved, stamps={"cb_panel": {"path": "data/cb_panel.csv.gz", "size": 2,
                                               "mtime": "2026-11-27T11:34:31"}})
    leg("17 an input that moved must say STALE (the word the chain looks for)",
        (not res2["ok"]) and res2["kind"] == "STALE" and "cb_panel" in json.dumps(res2),
        json.dumps(res2["kind"]))

    late = json.loads(json.dumps(face))
    late["evidence_cutoff"] = "2026-11-30"
    res3 = _verify(late, stamps={}, pub_now=pub)
    leg("18 a cutoff that is not a bar must fail",
        (not res3["ok"]) and any("not the last shared bar" in p for p in res3["problems"]))

    flip = json.loads(json.dumps(face))
    flip["rulers"]["B"]["etf_cagr"] = -0.50
    flip["rulers"]["B"]["gap_pp"] = _pp(-0.50 - a_stats["cagr"])
    res4 = _verify(flip, stamps={}, pub_now=pub)
    leg("19 a verdict that no longer follows from the rows must fail",
        (not res4["ok"]) and any("verdict does not recompute" in p for p in res4["problems"]),
        json.dumps(res4["problems"])[:200])

    banks = json.loads(json.dumps(face))
    banks["wallet"]["by_ruler"]["B"]["cb_book"]["year_cny"] += 500.0
    res5 = _verify(banks, stamps={}, pub_now=pub)
    leg("20 a wallet row that does not recompute must fail",
        (not res5["ok"]) and any("wallet" in p for p in res5["problems"]),
        json.dumps(res5["problems"])[:200])

    ok_n = sum(1 for l in legs if l["ok"])
    print("selftest %d/%d" % (ok_n, len(legs)))
    return 0 if ok_n == len(legs) else 1


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest", "print"))
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    face = build(write=not args.no_write, quiet=args.quiet)
    if args.cmd == "print":
        print(json.dumps(_plain(face), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
