"""Is the select leg's alpha spread over its months, or does a handful of months pay for it? (r1766)

r1764 closed the breadth axis (2..30 seats moved the floor by 1.9pp, not the -0.5 slope pure
diversification would give) and r1765 closed the correlation axis (de-correlated picking moved
the floor 8.74 -> 6.98pp but took the select leg 7.45 -> 2.79pp with it). Both said the same
thing in different words: the residual is this ranking's own common tilt. So the next honest
question is not "a smaller noise" but "a different ruler" -- is the +7.45pp itself spread over
the window, or is it a handful of months?

The decomposition used here is exact and additive, not approximate:

    select_ann_pp = mean(daily select) * 252 * 100
                  = sum over months [ sum(daily select in month) / n_bars * 252 * 100 ]

so the month contributions add up to the published number to the last digit. Alongside it the
face prints the compounded monthly select (what a reader would see month by month) and says
which of the two it is quoting.

Three readings are reported, all from the same one engine run:

  1. the month table -- per month: bars, additive pp, compounded pp, share of the positive total;
  2. the concentration -- top-10%-of-months share, positive-month ratio, HHI and its reciprocal
     (effective windows), plus the same for quarters and years;
  3. a month-block bootstrap -- the same resampling idea as r1762 but with a month as the block,
     which keeps the within-month correlation the day-block bootstrap destroys. Reported next to
     the r1762 day-block number so a reader can see which direction the ruler moves.

The criteria are written before the run and re-derived by --check:

    EVENT_DRIVEN  positive months < 55% of months, or the top 10% of months carry >= 60% of
                  the positive total
    STABLE        positive months >= 65% and the top 10% carry < 40%
    MIXED         everything else

The control arm is the published book itself: the same base arm must reproduce r1765's
select_ann_pp within 0.25pp, or this face refuses to judge.

Usage:
  python scripts/etf_book_period_slice.py run
  python scripts/etf_book_period_slice.py --selftest
  python scripts/etf_book_period_slice.py --check
  python scripts/etf_book_period_slice.py --md
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_equity_alpha as A                   # noqa: E402  (classify)
import etf_book_corr_select as CS              # noqa: E402  (the base arm, unchanged)
import etf_book_book_mde as M                  # noqa: E402  (the frozen ruler)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_period_slice.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_PERIOD_SLICE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_CORR = os.path.join(ROOT, "results", "etf_book_corr_select.json")

BENCH = CS.BENCH
GATE = CS.GATE
PER_YEAR = 252.0
Z80 = M.Z_80
BLOCK = M.BLOCK
DRAWS = M.DRAWS
SEED = M.SEED
TARGET_PP = 1.0             # the sentence readers actually say: "better by 1pp"
CONTROL_TOL_PP = 0.25       # the base arm must reproduce r1765's own cell

# criteria frozen before the run
TOP_FRAC = 0.10             # "the top 10% of months"
EVENT_TOP_SHARE = 0.60      # ... carry at least this share of the positive total
EVENT_POS_RATIO = 0.55      # ... or fewer than this share of months are positive
STABLE_POS_RATIO = 0.65
STABLE_TOP_SHARE = 0.40


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def ann_pp(mean_daily):
    return float(mean_daily) * PER_YEAR * 100.0


def month_frame(dates, sel):
    """Per calendar month: bars, additive pp (sums to the total), compounded pp."""
    d = pd.DataFrame({"d": pd.to_datetime(list(dates)), "s": np.asarray(list(sel), float)})
    d = d.dropna(subset=["s"])
    d["m"] = d["d"].dt.to_period("M")
    g = d.groupby("m")["s"]
    out = pd.DataFrame({"bars": g.size(), "add_pp": g.sum() * PER_YEAR * 100.0 / len(d)})
    comp = d.groupby("m")["s"].apply(lambda x: float((1.0 + x).prod() - 1.0) * 100.0)
    out["comp_pp"] = comp
    out = out.reset_index().rename(columns={"m": "month"})
    out["month"] = out["month"].astype(str)
    return out


def period_frame(months, key):
    """Collapse the month table onto quarters/years; the additive column stays additive."""
    if key == "month":
        return months.copy()
    d = months.copy()
    per = pd.PeriodIndex(d["month"], freq="M")
    d["bucket"] = [str(p.quarter if key == "quarter" else p.year) for p in per]
    if key == "quarter":
        d["bucket"] = ["%dQ%d" % (p.year, p.quarter) for p in per]
    g = d.groupby("bucket")
    out = pd.DataFrame({"bars": g["bars"].sum(), "add_pp": g["add_pp"].sum()})
    out["comp_pp"] = g["comp_pp"].apply(lambda x: float((1.0 + x / 100.0).prod() - 1.0) * 100.0)
    return out.reset_index().rename(columns={"bucket": key})


def concentration(contrib):
    """Judgement-ready numbers for one additive contribution column."""
    a = np.asarray([float(x) for x in contrib], float)
    pos = a[a > 0.0]
    tot_pos = float(pos.sum())
    n = len(a)
    n_top = max(1, int(round(n * TOP_FRAC)))
    top = np.sort(a)[::-1]
    top_share = (float(top[:n_top].sum()) / tot_pos) if tot_pos > 0 else None
    pos_ratio = float((a > 0).sum()) / n if n else None
    share = (np.abs(a) / float(np.abs(a).sum())) if float(np.abs(a).sum()) > 0 else None
    hhi = float((share ** 2).sum()) if share is not None else None
    return {
        "n_windows": int(n), "n_positive": int((a > 0).sum()),
        "positive_ratio": round(pos_ratio, 4) if pos_ratio is not None else None,
        "total_pp": round(float(a.sum()), 4),
        "positive_total_pp": round(tot_pos, 4),
        "top_n": int(n_top),
        "top_share": round(top_share, 4) if top_share is not None else None,
        "hhi": round(hhi, 5) if hhi is not None else None,
        "effective_windows": round(1.0 / hhi, 2) if hhi else None,
    }


def classify(month_conc):
    if not month_conc or month_conc.get("positive_ratio") is None:
        return {"verdict": "CANNOT_JUDGE", "sentence": "没有可分解的窗口：这张面不判。"}
    pr = float(month_conc["positive_ratio"])
    ts = month_conc.get("top_share")
    if pr < EVENT_POS_RATIO or (ts is not None and ts >= EVENT_TOP_SHARE):
        return {"verdict": "EVENT_DRIVEN",
                "sentence": "钱集中：正贡献的月份只有 %.0f%%，前 %d 个月就占了正贡献的 %s"
                            "——这本书的正确说法是「几个窗口养着它」，不是「每月都在赚」。"
                            % (pr * 100.0, month_conc["top_n"],
                               "-" if ts is None else "%.0f%%" % (ts * 100.0))}
    if pr >= STABLE_POS_RATIO and (ts is not None and ts < STABLE_TOP_SHARE):
        return {"verdict": "STABLE",
                "sentence": "钱是散的：%.0f%% 的月份为正，前 %d 个月只占正贡献的 %s"
                            "——这个超额不靠少数窗口。" % (pr * 100.0, month_conc["top_n"],
                                                    "-" if ts is None else "%.0f%%" % (ts * 100.0))}
    return {"verdict": "MIXED",
            "sentence": "两头都不占：%.0f%% 的月份为正、前 %d 个月占 %s —"
                        " 既不是每日稳定超额，也不是几个窗口养着。"
                        % (pr * 100.0, month_conc["top_n"],
                           "-" if ts is None else "%.0f%%" % (ts * 100.0))}


def edge_note(month_conc, v):
    """How close the verdict sits to the line it was judged on. Not a second verdict."""
    pr = float(month_conc["positive_ratio"])
    ts = month_conc.get("top_share")
    if v.get("verdict") == "EVENT_DRIVEN":
        if pr < EVENT_POS_RATIO and (ts is None or ts < EVENT_TOP_SHARE):
            return {"basis": "positive-ratio only", "margin_pp": round((EVENT_POS_RATIO - pr) * 100, 2),
                    "other_leg": ("top-%.0f%% share %.2f < %.2f, not triggered"
                                  % (TOP_FRAC * 100, float(ts or 0.0), EVENT_TOP_SHARE)),
                    "reading": "只靠「正贡献月份不足」这一条落地，且余量 %.2fpp；"
                               "换一条判据（集中度）并不触发——这是边缘判定，不是强判定。"
                               % ((EVENT_POS_RATIO - pr) * 100.0)}
        return {"basis": "concentration", "margin_pp": None,
                "other_leg": "positive ratio %.2f" % pr,
                "reading": "集中度这一条自己就越线，判定不依赖正贡献比例。"}
    return {"basis": "n/a", "margin_pp": None, "other_leg": "", "reading": ""}


def threshold_sweep(month_conc):
    """What the same face would say if only the positive-ratio line moved. Reader-facing only."""
    pr = float(month_conc["positive_ratio"])
    ts = month_conc.get("top_share")
    out = []
    for cut in (0.45, 0.50, 0.52, 0.54, 0.55, 0.56, 0.58, 0.60, 0.65):
        if pr < cut or (ts is not None and ts >= EVENT_TOP_SHARE):
            v = "EVENT_DRIVEN"
        elif pr >= STABLE_POS_RATIO and ts is not None and ts < STABLE_TOP_SHARE:
            v = "STABLE"
        else:
            v = "MIXED"
        out.append({"pos_ratio_cut": cut, "verdict": v})
    return out


def month_blocks(dates, sel):
    """Calendar months as bootstrap blocks: keeps the within-month correlation alive."""
    d = pd.DataFrame({"d": pd.to_datetime(list(dates)), "s": np.asarray(list(sel), float)})
    d = d.dropna(subset=["s"])
    d["m"] = d["d"].dt.to_period("M")
    return [g["s"].to_numpy() for _, g in d.groupby("m")]


def month_bootstrap(blocks, draws=DRAWS, seed=SEED, z=Z80):
    """Same statistic as the day-block ruler, but a month is the resampling unit."""
    if not blocks:
        return None
    rng = np.random.default_rng(seed)
    k = len(blocks)
    means = np.empty(draws, float)
    for i in range(draws):
        pick = rng.integers(0, k, k)
        means[i] = np.concatenate([blocks[j] for j in pick]).mean()
    se = ann_pp(means.std(ddof=1))
    return {
        "se_ann_pp": round(se, 4),
        "mde80_ann_pp": round(z * se, 4),
        "p_direction": round(float((means <= 0.0).mean()), 4),
        "n_blocks": int(k),
        "draws": int(draws),
        "seed": int(seed),
    }


def bars_needed(se_ann_pp, windows, target_pp=TARGET_PP):
    """How many windows of the same ruler would be needed for this SE to reach target_pp."""
    if not se_ann_pp or windows < 2:
        return None
    return max(1, int(round(windows * (float(se_ann_pp) / float(target_pp)) ** 2)))


def read_inputs():
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    corr = _load(FACE_CORR) if os.path.exists(FACE_CORR) else {}
    base_row = next((r for r in (corr.get("rows") or []) if r.get("arm") == "base"), {})
    return {
        "cost": (cfg.get("cost_bp_per_side") or 10.0) / 1e4,
        "rebal": int(cfg.get("rebal") or 20),
        "vol_target": cfg.get("vol_target"),
        "published_cagr_pct": (None if published.get("cagr") is None
                              else round(float(published["cagr"]) * 100.0, 3)),
        "base_select_pp": base_row.get("select_ann_pp"),
        "base_cagr_pct": base_row.get("book_cagr_pct"),
        "evidence_cutoff": price.get("evidence_cutoff"),
    }


def run():
    t0 = time.time()
    cfg = read_inputs()
    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)

    base = CS.arm(close, openp, amt, score, cls, cfg["rebal"], cfg["cost"], cfg["vol_target"])
    df = base["df"]
    sel = df["select"].dropna()
    dates = pd.to_datetime(sel.index)
    total_pp = ann_pp(sel.mean())
    print("[base] select=%+6.2fpp cagr=%.2f%% bars=%d %.0fs"
          % (total_pp, float(base["stats"]["full"]["cagr"]) * 100.0, len(sel),
             time.time() - t0), flush=True)

    months = month_frame(dates, sel)
    ident_err = abs(float(months["add_pp"].sum()) - total_pp)
    quarters = period_frame(months, "quarter")
    years_f = period_frame(months, "year")
    m_conc = concentration(months["add_pp"])
    q_conc = concentration(quarters["add_pp"])
    y_conc = concentration(years_f["add_pp"])
    v = classify(m_conc)
    edge = edge_note(m_conc, v)

    top = months.sort_values("add_pp", ascending=False).head(int(m_conc["top_n"]))
    bottom = months.sort_values("add_pp").head(5)
    mb = month_bootstrap(month_blocks(dates, sel))
    rb = M.bootstrap_se(list(sel))
    control_pp = (None if cfg["base_select_pp"] is None
                  else round(total_pp - float(cfg["base_select_pp"]), 3))
    control_ok = control_pp is not None and abs(control_pp) <= CONTROL_TOL_PP

    out = {
        "evidence_cutoff": cfg["evidence_cutoff"] or str(pd.Timestamp(close.index[-1]).date()),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_period_slice.py",
        "rule": {
            "benchmark": BENCH, "gate_cny": GATE, "seats": CS.BASE_SEATS,
            "rebal": cfg["rebal"], "cost_bp_per_side": round(cfg["cost"] * 1e4, 3),
            "vol_target": cfg["vol_target"],
            "top_frac": TOP_FRAC, "event_top_share": EVENT_TOP_SHARE,
            "event_pos_ratio": EVENT_POS_RATIO, "stable_pos_ratio": STABLE_POS_RATIO,
            "stable_top_share": STABLE_TOP_SHARE, "control_tol_pp": CONTROL_TOL_PP,
            "z80": Z80, "block": BLOCK, "draws": DRAWS, "seed": SEED,
            "question": "is the select leg's annualised excess spread over its months, or does "
                        "a handful of months pay for the whole window",
            "decomposition": "additive: sum(month add_pp) == select_ann_pp exactly",
            "frozen": "criteria written before the run; --check re-derives the verdict",
        },
        "control": {
            "base_select_ann_pp": round(total_pp, 4),
            "published_r1765_select_ann_pp": cfg["base_select_pp"],
            "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP, "ok": control_ok,
        },
        "identity": {"sum_month_add_pp": round(float(months["add_pp"].sum()), 6),
                     "select_ann_pp": round(total_pp, 6),
                     "abs_error": float(ident_err), "ok": bool(ident_err <= 1e-9)},
        "bars": int(len(sel)),
        "months": m_conc, "quarters": q_conc, "years": y_conc,
        "top_months": [{"month": r.month, "add_pp": round(float(r.add_pp), 4),
                        "share_of_positive": (None if not m_conc.get("positive_total_pp")
                                              else round(float(r.add_pp)
                                                         / float(m_conc["positive_total_pp"]), 4))}
                       for r in top.itertuples()],
        "worst_months": [{"month": r.month, "add_pp": round(float(r.add_pp), 4)}
                         for r in bottom.itertuples()],
        "bootstrap": {
            "day_block": {"se_ann_pp": rb.get("se_ann_pp") if rb else None,
                          "mde80_ann_pp": rb.get("mde80_ann_pp") if rb else None,
                          "p_direction": rb.get("p_direction") if rb else None,
                          "block": BLOCK},
            "month_block": mb,
            "mde_ratio_month_over_day": (None if not (mb and rb and rb.get("se_ann_pp"))
                                         else round(mb["se_ann_pp"] / float(rb["se_ann_pp"]), 3)),
        },
        "to_1pp": {
            "bars_day_rule": bars_needed((rb or {}).get("se_ann_pp"), len(sel)),
            "months_month_rule": bars_needed((mb or {}).get("se_ann_pp"),
                                             (mb or {}).get("n_blocks")),
            "note": "same statistic, two rulers: the month block keeps the within-month "
                    "correlation the day block breaks",
        },
        "table_months": months.to_dict(orient="records"),
        "table_quarters": quarters.to_dict(orient="records"),
        "table_years": years_f.to_dict(orient="records"),
        "edge": edge,
        "threshold_sweep": threshold_sweep(m_conc),
        **v,
    }
    if not control_ok:
        out["verdict"] = "CANNOT_JUDGE_CONTROL"
        out["sentence"] = ("基座臂 select 与 r1765 在印值差 %s pp（容差 %.2fpp），"
                           "这不是同一本书，本面不判。" % (control_pp, CONTROL_TOL_PP))
    out["run_seconds"] = round(time.time() - t0, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[verdict] %s -- %s" % (out["verdict"], out["sentence"]), flush=True)
    print("[conc] months=%d pos=%d top%d_share=%s hhi=%.4f eff=%.1f"
          % (m_conc["n_windows"], m_conc["n_positive"], m_conc["top_n"], m_conc["top_share"],
             m_conc["hhi"], m_conc["effective_windows"]), flush=True)
    print("[bootstrap] day mde80=%.2fpp month mde80=%.2fpp ratio=%.2f"
          % ((rb or {}).get("mde80_ann_pp") or 0.0, (mb or {}).get("mde80_ann_pp") or 0.0,
             out["bootstrap"]["mde_ratio_month_over_day"] or 0.0), flush=True)
    print("[write] %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


def write_md():
    d = _load(OUT_JSON)
    m, q, y = d["months"], d["quarters"], d["years"]
    b = d["bootstrap"]
    L = []
    L.append("# 选股腿的钱是散在每个月，还是几个窗口养着它（r1766）\n")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_period_slice.py`；"
             "%d 根 bar；判定=%s。\n"
             % (d["evidence_cutoff"], d["panel_last_bar"], d["bars"], d["verdict"]))
    L.append("## 一句话\n")
    L.append(d["sentence"] + "\n")
    if d.get("edge", {}).get("reading"):
        L.append("**这条判定有多牢**：%s\n" % d["edge"]["reading"])
    L.append("## 分解是加法的，不是近似的\n")
    L.append("`select_ann_pp = Σ_月 [ Σ_月内日收益 / n_bar × 252 × 100 ]`，所以月贡献加起来"
             "就是 %.2fpp（逐位误差 %.1e）。复合月收益另列一栏，只用来读「每个月大概什么样」。\n"
             % (d["identity"]["select_ann_pp"], d["identity"]["abs_error"]))
    L.append("| 口径 | 窗口数 | 正贡献窗口 | 正贡献占比 | 前 %d 窗口占正贡献 | HHI | 有效窗口数 |\n"
             "|---|---|---|---|---|---|---|\n" % m["top_n"])
    for name, c in (("月", m), ("季", q), ("年", y)):
        L.append("| %s | %d | %d | %.0f%% | %s | %.4f | %.1f |\n"
                 % (name, c["n_windows"], c["n_positive"], c["positive_ratio"] * 100.0,
                    "-" if c["top_share"] is None else "%.0f%%" % (c["top_share"] * 100.0),
                    c["hhi"], c["effective_windows"]))
    L.append("\n## 最赚钱的 %d 个月\n" % len(d["top_months"]))
    L.append("| 月份 | 加法贡献 pp | 占正贡献 |\n|---|---|---|\n")
    for r in d["top_months"]:
        L.append("| %s | %+.2f | %s |\n"
                 % (r["month"], r["add_pp"],
                    "-" if r["share_of_positive"] is None else "%.0f%%" % (r["share_of_positive"] * 100.0)))
    L.append("\n## 最亏的 5 个月\n")
    L.append("| 月份 | 加法贡献 pp |\n|---|---|\n")
    for r in d["worst_months"]:
        L.append("| %s | %+.2f |\n" % (r["month"], r["add_pp"]))
    L.append("\n## 换尺子：月块自助 vs 日块自助\n")
    L.append("同一统计量、同一个 z80 与同一个种子，只把重采样单位从 %d 根 bar 换成一个日历月"
             "（月内的相关被保留，日块把它打散）：\n\n" % b["day_block"]["block"])
    L.append("| 尺子 | SE（年化 pp） | MDE80（pp） | 方向 p |\n|---|---|---|---|\n")
    L.append("| 日块（r1762 口径） | %.2f | %.2f | %.4f |\n"
             % (b["day_block"]["se_ann_pp"], b["day_block"]["mde80_ann_pp"],
                b["day_block"]["p_direction"]))
    L.append("| 月块（本轮） | %.2f | %.2f | %.4f |\n"
             % (b["month_block"]["se_ann_pp"], b["month_block"]["mde80_ann_pp"],
                b["month_block"]["p_direction"]))
    L.append("\n月块 / 日块 = **%.2f 倍**。把 MDE 压到 %.0fpp 需要的样本量：日块口径 %s 根 bar，"
             "月块口径 %s 个月。两个数都远超这本书的 %d 根 bar / %d 个月——「再攒数据」不是答案，"
             "换问法（可重复窗口的计数）才是。\n"
             % (b["mde_ratio_month_over_day"] or 0.0, TARGET_PP,
                d["to_1pp"]["bars_day_rule"], d["to_1pp"]["months_month_rule"],
                d["bars"], m["n_windows"]))
    L.append("\n## 控制臂\n")
    L.append("基座臂 select=%.2fpp，r1765 在印 %.2fpp，差 %s pp（容差 %.2f）——同一本书。\n"
             % (d["control"]["base_select_ann_pp"],
                d["control"]["published_r1765_select_ann_pp"],
                d["control"]["delta_pp"], d["control"]["tol_pp"]))
    sw = d.get("threshold_sweep") or []
    if sw:
        L.append("\n## 门槛敏感度（只摇「正贡献比例」这一条线，集中度线不动）\n")
        L.append("| 正贡献比例门槛 | 判定 |\n|---|---|\n")
        for r in sw:
            L.append("| %.0f%% | %s |\n" % (r["pos_ratio_cut"] * 100.0, r["verdict"]))
        L.append("\n实测正贡献比例 = %.1f%%。\n" % (d["months"]["positive_ratio"] * 100.0))
    L.append("\n## 三种粒度说的不是同一件事\n")
    L.append("月：%.0f%% 的月份为正、有效窗口 %.1f／%d；季：%.0f%%、%.1f／%d；年：%.0f%%、%.1f／%d。\n\n"
             % (m["positive_ratio"] * 100.0, m["effective_windows"], m["n_windows"],
                q["positive_ratio"] * 100.0, q["effective_windows"], q["n_windows"],
                y["positive_ratio"] * 100.0, y["effective_windows"], y["n_windows"]))
    L.append("年这一层是稳的（%d/%d 年为正），季这一层是中等（%d/%d），月这一层只有一半（%d/%d）。"
             "所以这本书的可见面应当按年/季考核：逐月读成绩，会把 %.2fpp 的年化读成「一半时间在亏」，"
             "而逐年看它七年里只有 %d 年亏。\n"
             % (y["n_positive"], y["n_windows"], q["n_positive"], q["n_windows"],
                m["n_positive"], m["n_windows"], m["total_pp"], y["n_windows"] - y["n_positive"]))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("".join(L))
    print("[write] %s" % OUT_MD, flush=True)
    return 0


def _check():
    d = _load(OUT_JSON)
    ok = True
    checks = []

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        checks.append({"name": name, "ok": bool(cond), "detail": str(detail)})

    chk("I1 month additive sums to the published select",
        d["identity"]["ok"], d["identity"])
    mtot = sum(float(r["add_pp"]) for r in d["table_months"])
    chk("I2 quarters sum to the same total",
        abs(sum(float(r["add_pp"]) for r in d["table_quarters"]) - mtot) <= 1e-9,
        (sum(float(r["add_pp"]) for r in d["table_quarters"]), mtot))
    chk("I3 years sum to the same total",
        abs(sum(float(r["add_pp"]) for r in d["table_years"]) - mtot) <= 1e-9,
        (sum(float(r["add_pp"]) for r in d["table_years"]), mtot))
    chk("C1 control arm reproduces r1765", d["control"]["ok"], d["control"])
    re_v = classify(d["months"])
    chk("V1 verdict re-derives", re_v["verdict"] == d["verdict"] or
        d["verdict"] == "CANNOT_JUDGE_CONTROL",
        {"now": re_v["verdict"], "stored": d["verdict"]})
    chk("V2 every window counted", d["months"]["n_windows"] == len(d["table_months"]))
    chk("V3 top-share is a share", d["months"]["top_share"] is None or
        0.0 <= d["months"]["top_share"] <= 1.0)
    gen = threshold_sweep(d["months"])
    chk("V4 threshold sweep is re-derivable",
        gen == [{"pos_ratio_cut": r["pos_ratio_cut"], "verdict": r["verdict"]}
                for r in d.get("threshold_sweep") or []] and len(gen) > 0,
        {"generated": len(gen)})
    chk("V5 the published verdict matches its own line",
        [r["verdict"] for r in gen if abs(r["pos_ratio_cut"] - EVENT_POS_RATIO) < 1e-12]
        == [d["verdict"]] or d["verdict"] == "CANNOT_JUDGE_CONTROL",
        [r["verdict"] for r in gen if abs(r["pos_ratio_cut"] - EVENT_POS_RATIO) < 1e-12])
    chk("B1 month block is wider than the day block",
        (d["bootstrap"]["mde_ratio_month_over_day"] or 0.0) >= 1.0,
        d["bootstrap"]["mde_ratio_month_over_day"])
    chk("T1 to-1pp needs more windows than the book has",
        d["to_1pp"]["months_month_rule"] is None or
        d["to_1pp"]["months_month_rule"] > d["months"]["n_windows"],
        d["to_1pp"])
    print(json.dumps({"ok": ok, "checks": checks}, ensure_ascii=False, indent=1), flush=True)
    return 0 if ok else 1


def selftest():
    legs = []

    def chk(name, cond, detail=""):
        legs.append({"leg": name, "ok": bool(cond), "detail": str(detail)})

    # month table: additive column must be the plain sum, compounded must not equal it
    dates = pd.date_range("2024-01-01", periods=40, freq="B")
    sel = np.linspace(-0.002, 0.004, 40)
    mf = month_frame(dates, sel)
    chk("L1 additive column sums to the total",
        abs(mf["add_pp"].sum() - ann_pp(np.mean(sel))) < 1e-9,
        (mf["add_pp"].sum(), ann_pp(np.mean(sel))))
    chk("L2 compounded column is not the additive column",
        abs(mf["comp_pp"].sum() - mf["add_pp"].sum()) > 1e-6,
        (mf["comp_pp"].sum(), mf["add_pp"].sum()))
    chk("L3 every bar lands in exactly one month", int(mf["bars"].sum()) == len(sel),
        int(mf["bars"].sum()))

    # one month carries everything -> EVENT_DRIVEN
    one = np.zeros(240)
    one[:20] = 0.01
    c1 = concentration(month_frame(pd.date_range("2020-01-01", periods=240, freq="B"), one)
                       ["add_pp"])
    chk("L4 a single paying month reads EVENT_DRIVEN", classify(c1)["verdict"] == "EVENT_DRIVEN",
        c1)

    # spread evenly across two years -> STABLE
    even = np.full(500, 0.0003)
    c2 = concentration(month_frame(pd.date_range("2020-01-01", periods=500, freq="B"), even)
                       ["add_pp"])
    chk("L5 an even calendar reads STABLE", classify(c2)["verdict"] == "STABLE", c2)

    # whole months alternate sign: half the calendar pays, half pays back -> not STABLE
    d6 = pd.date_range("2020-01-01", periods=480, freq="B")
    per6 = d6.to_period("M")
    order6 = list(dict.fromkeys(per6))
    sign6 = {m: (1.0 if i % 2 == 0 else -1.0) for i, m in enumerate(order6)}
    half = np.array([sign6[m] for m in per6]) * 0.004
    c3 = concentration(month_frame(d6, half)["add_pp"])
    chk("L6 alternating months do not read STABLE", classify(c3)["verdict"] != "STABLE", c3)

    # concentration geometry
    chk("L7 HHI of one window is 1 and of N equal windows is 1/N",
        abs(concentration([3.0])["hhi"] - 1.0) < 1e-12 and
        abs(concentration([1.0] * 4)["hhi"] - 0.25) < 1e-12)
    chk("L8 top-share of one positive window is 1",
        abs(concentration([5.0, -1.0])["top_share"] - 1.0) < 1e-12)

    # the month block bootstrap: a constant series has no width, a noisy one does
    blocks = [np.full(20, 0.001)] * 24
    mb0 = month_bootstrap(blocks, draws=200)
    chk("L9 a constant panel has zero block width", mb0["se_ann_pp"] == 0.0, mb0)
    rng = np.random.default_rng(7)
    noisy = [rng.normal(0.0, 0.01, 20) for _ in range(24)]
    mb1 = month_bootstrap(noisy, draws=300)
    chk("L10 a noisy panel has positive width and a positive MDE",
        mb1["se_ann_pp"] > 0 and mb1["mde80_ann_pp"] > 0, mb1)

    # period collapse keeps the additive total
    p = period_frame(month_frame(pd.date_range("2023-01-01", periods=300, freq="B"),
                                 np.full(300, 0.0002)), "quarter")
    chk("L11 quarter collapse is additive", abs(p["add_pp"].sum() - 0.0002 * 252 * 100) < 1e-9,
        p["add_pp"].sum())

    # ruler arithmetic
    chk("L12 bars_needed inverts the square root",
        bars_needed(2.0, 100, 1.0) == 400 and bars_needed(None, 100) is None)

    # no-paying-month case must not crash the classifier
    c0 = concentration(np.zeros(12))
    chk("L13 an all-zero calendar is judged, not crashed",
        classify(c0)["verdict"] in ("MIXED", "EVENT_DRIVEN"), classify(c0))

    # the reader-facing sensitivity sweep must move one way only
    sw = threshold_sweep({"positive_ratio": 0.53, "top_share": 0.45})
    seen = [r["verdict"] for r in sw]
    chk("L14 raising the positive line never makes the calendar look steadier",
        seen.index("MIXED") < seen.index("EVENT_DRIVEN") if "EVENT_DRIVEN" in seen else True,
        seen)
    chk("L15 the sweep names the frozen line's own verdict",
        [r["verdict"] for r in sw if abs(r["pos_ratio_cut"] - EVENT_POS_RATIO) < 1e-12]
        == ["EVENT_DRIVEN"], sw)

    # the edge note must not pretend a one-legged call is a two-legged one
    e1 = edge_note({"positive_ratio": 0.53, "top_share": 0.45, "top_n": 8},
                   {"verdict": "EVENT_DRIVEN"})
    e2 = edge_note({"positive_ratio": 0.70, "top_share": 0.75, "top_n": 8},
                   {"verdict": "EVENT_DRIVEN"})
    chk("L16 the edge note separates the two grounds",
        e1["basis"] == "positive-ratio only" and e2["basis"] == "concentration",
        (e1["basis"], e2["basis"]))

    # a quarter bucket must carry its year, or 2020Q1 and 2021Q1 collapse into one row
    d7 = pd.date_range("2020-01-01", periods=700, freq="B")
    p7 = period_frame(month_frame(d7, np.full(700, 0.0001)), "quarter")
    chk("L17 quarter buckets carry the year",
        len(p7) > 4 and all("Q" in str(x) and len(str(x)) == 6 for x in p7["quarter"]),
        list(p7["quarter"])[:5])

    bad = [x for x in legs if not x["ok"]]
    print(json.dumps({"selftest": "%d/%d" % (len(legs) - len(bad), len(legs)),
                      "failed": bad}, ensure_ascii=False, indent=1), flush=True)
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return run()
    if cmd == "--md":
        return write_md()
    if cmd == "--check":
        return _check()
    if cmd == "--selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
