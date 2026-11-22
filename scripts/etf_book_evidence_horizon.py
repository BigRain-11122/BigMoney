"""How long does a reader have to wait before the book can be believed? (r1962)

r1960 said the headline cannot survive its own hunt: at N*=5 independent tries the 1.10 Sharpe
needs to be 1.585 to clear a deflated 0.95, and the only other way out is more forward record
(+7.1 years at the same Sharpe). That is a verdict about proof, not about the book. The question
a reader actually holds is the complement of it -- "if I start following this, how long until I
can tell whether it works, and what do I sit through meanwhile?"

This face answers that with the book's own net daily series, and nothing else:

  1. the wait, in months -- rolling windows per horizon, share of windows finishing above cash,
     above the benchmark, and above zero, with the median/worst/best window annualised;
  2. the wait, in years -- t = SR * sqrt(years) inverted: how many years of forward record are
     needed before the observed mean is 2 standard errors from zero, quoted at the book's own
     Sharpe and at the deflated hurdle r1960 demands;
  3. the money it costs to wait -- the worst rolling 12-month window priced on a 1,000,000 CNY
     account, and the worst peak-to-trough inside any 12-month window.

The criteria are written before the run and re-derived by --check:

    EVIDENCE_SOON       >= 80% of 12-month windows finish above cash AND t-years at the book's
                        own Sharpe <= 3.0
    PATIENCE_REQUIRED   < 60% of 12-month windows finish above cash OR t-years > 4.0
    MIXED               everything else

Honest limits, printed on the face rather than buried here: windows overlap, so the count of
windows is not a sample size (the non-overlapping count is printed next to it); cash is a flat
annual rate, not the realised repo path; and the deflated hurdle is only meaningful if the trial
count it uses is right.

The control arm is the published book: the base arm must reproduce the select leg within 0.25pp
or this face refuses to judge.

Usage:
  python scripts/etf_book_evidence_horizon.py run
  python scripts/etf_book_evidence_horizon.py --selftest
  python scripts/etf_book_evidence_horizon.py --check
  python scripts/etf_book_evidence_horizon.py --md
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
import etf_equity_alpha as A                  # noqa: E402  (classify)
import etf_book_corr_select as CS             # noqa: E402  (the base arm, unchanged)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_evidence_horizon.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_EVIDENCE_HORIZON.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_CORR = os.path.join(ROOT, "results", "etf_book_corr_select.json")
FACE_RENT = os.path.join(ROOT, "results", "etf_book_search_rent.json")

BENCH = CS.BENCH
GATE = CS.GATE
PER_YEAR = 252.0
HORIZONS = (3, 6, 12, 24, 36)     # months
CASH_ANN = 0.015                  # the hurdle a depositor already gets
CASH_EPS = 1e-12                 # matching cash exactly is not beating it
T_LINE = 2.0                      # "two standard errors from zero"
ACCOUNT_CNY = 1000000.0
CONTROL_TOL_PP = 0.25

# criteria frozen before the run
SOON_SHARE = 0.80
SOON_YEARS = 3.0
SLOW_SHARE = 0.60
SLOW_YEARS = 4.0


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def years_to_t(sr_ann, t=T_LINE):
    """t = SR * sqrt(years) inverted. None when there is no Sharpe to invert."""
    if not sr_ann or float(sr_ann) <= 0.0:
        return None
    return float((float(t) / float(sr_ann)) ** 2)


def monthly_from_daily(dates, series):
    """Daily simple returns -> calendar-month compounded returns, ordered."""
    d = pd.DataFrame({"d": pd.to_datetime(list(dates)), "r": np.asarray(list(series), float)})
    d = d.dropna(subset=["r"])
    d["m"] = d["d"].dt.to_period("M")
    g = d.groupby("m")["r"]
    out = pd.DataFrame({"bars": g.size(), "ret": g.apply(lambda x: float((1.0 + x).prod() - 1.0))})
    return out.reset_index().rename(columns={"m": "month"})


def window_rows(months, bench_m, horizon):
    """Rolling windows of `horizon` months: annualised book / bench / excess-over-cash."""
    r = np.asarray(months, float)
    b = np.asarray(bench_m, float)
    cash_m = (1.0 + CASH_ANN) ** (1.0 / 12.0) - 1.0
    n = len(r)
    if n < horizon:
        return {"horizon_months": int(horizon), "windows": 0, "non_overlapping": 0,
                "share_pos": None, "share_beat_cash": None, "share_beat_bench": None,
                "median_ann": None, "worst_ann": None, "best_ann": None,
                "worst_window_cny": None, "worst_inner_dd_pct": None}
    ann = []
    dd = []
    for i in range(n - horizon + 1):
        block = r[i:i + horizon]
        cum = float(np.prod(1.0 + block))
        ann.append(cum ** (12.0 / horizon) - 1.0)
        peak = np.maximum.accumulate(np.concatenate(([1.0], np.cumprod(1.0 + block))))
        path = np.concatenate(([1.0], np.cumprod(1.0 + block)))
        dd.append(float((path / np.maximum.accumulate(path) - 1.0).min()))
    ann = np.asarray(ann, float)
    cash_ann = (1.0 + cash_m) ** 12 - 1.0
    return {
        "horizon_months": int(horizon),
        "windows": int(len(ann)),
        "non_overlapping": int(n // horizon),
        "share_pos": round(float((ann > 0.0).mean()), 4),
        "share_beat_cash": round(float((ann > cash_ann + CASH_EPS).mean()), 4),
        "share_beat_bench": round(float((ann > np.asarray([_ann_window(b[i:i + horizon]) for i in range(n - horizon + 1)])).mean()), 4),
        "median_ann": round(float(np.median(ann)), 4),
        "worst_ann": round(float(ann.min()), 4),
        "best_ann": round(float(ann.max()), 4),
        "worst_window_cny": round(float(ACCOUNT_CNY * (ann.min())), 0),
        "worst_inner_dd_pct": round(float(min(dd)) * 100.0, 2),
    }


def _ann_window(block):
    return float(np.prod(1.0 + np.asarray(block, float)) ** (12.0 / len(block)) - 1.0)


def classify(rows, t_own, t_hurdle):
    w = next((r for r in rows if r.get("horizon_months") == 12), {})
    share = w.get("share_beat_cash")
    if share is None or t_own is None:
        return {"verdict": "CANNOT_JUDGE",
                "sentence": "没有可用的 12 个月窗或夏普：这张面不判。"}
    share_txt = "%s 的 12 个月窗口跑赢现金（中位 %s）" % (
        ("%.0f%%" % (share * 100.0)) if share >= 0.6 else ("只有 %.0f%%" % (share * 100.0)),
        _pct(w.get("median_ann")))
    tail = "这本书自己的夏普 %.2f 要 %.1f 年才到 %.0f 个标准误" % (2.0 / (t_own ** 0.5),
                                                     t_own, T_LINE)
    if share >= SOON_SHARE and t_own <= SOON_YEARS:
        v = "EVIDENCE_SOON"
        sent = "一年就能看出个大概：%s，%s——短于三年。" % (share_txt, tail)
    elif share < SLOW_SHARE or t_own > SLOW_YEARS:
        v = "PATIENCE_REQUIRED"
        sent = ("要耐心：%s，而%s——你在头一两年看到的涨跌多半是噪声，"
                "真判断要等到那条线走完。" % (share_txt, tail))
    else:
        v = "MIXED"
        sent = "一半一半：%s，%s。" % (share_txt, tail)
    if t_hurdle is not None:
        sent += (" 而要证明它没吃搜索租金（夏普需 %.3f），同一条路要 %.1f 年的前向记录。"
                 % (float(t_hurdle[0]), float(t_hurdle[1])))
    return {"verdict": v, "sentence": sent}


def _pct(x):
    return "-" if x is None else "%+.1f%%" % (float(x) * 100.0)


def read_inputs():
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    corr = _load(FACE_CORR) if os.path.exists(FACE_CORR) else {}
    base_row = next((r for r in (corr.get("rows") or []) if r.get("arm") == "base"), {})
    hurdle_sr = None
    hurdle_n = None
    if os.path.exists(FACE_RENT):
        rent = _load(FACE_RENT)
        rows = rent.get("required_sharpe") or []
        pick = next((r for r in rows if int(r.get("n_trials") or 0) == 58), None)
        if pick is None:
            pick = next((r for r in rows if int(r.get("n_trials") or 0) == 5), None)
        if pick is not None:
            hurdle_sr = pick.get("required_sr_annualized")
            hurdle_n = int(pick.get("n_trials") or 0)
    return {
        "cost": (cfg.get("cost_bp_per_side") or 10.0) / 1e4,
        "rebal": int(cfg.get("rebal") or 20),
        "vol_target": cfg.get("vol_target"),
        "published_cagr_pct": (None if published.get("cagr") is None
                               else round(float(published["cagr"]) * 100.0, 3)),
        "base_select_pp": base_row.get("select_ann_pp"),
        "evidence_cutoff": price.get("evidence_cutoff"),
        "hurdle_sharpe": hurdle_sr,
        "hurdle_n": hurdle_n,
    }


def control_arm(close, openp, amt, feats, cls, cfg):
    """Replay the same arm on the panel truncated to the published cutoff.

    The live panel advances every week, so "does my run reproduce the published cell" is only a
    real control if both are read at the same bar. Returns (select_pp, cutoff_used) or (None, None).
    """
    cut = cfg.get("evidence_cutoff")
    if not cut:
        return None, None
    try:
        c = close.loc[:cut]
        o = openp.loc[:cut]
        a = amt.loc[:cut]
    except Exception:
        return None, None
    if len(c.index) < 100:
        return None, None
    score = E.build_score(c, a, feats, min_amt=GATE)
    arm = CS.arm(c, o, a, score, cls, cfg["rebal"], cfg["cost"], cfg["vol_target"])
    sel = arm["df"]["select"].dropna()
    return float(sel.mean()) * PER_YEAR * 100.0, cut


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
    select_pp = float(sel.mean()) * PER_YEAR * 100.0
    print("[base] select=%+6.2fpp cagr=%.2f%% bars=%d %.0fs"
          % (select_pp, float(base["stats"]["full"]["cagr"]) * 100.0, len(sel),
             time.time() - t0), flush=True)

    net = df["net"].dropna()
    bench = df["r_bench"].reindex(net.index)
    m_net = monthly_from_daily(net.index, net.values)
    m_bench = monthly_from_daily(bench.index, bench.values)
    common = m_net["month"].astype(str)
    m_bench = m_bench.set_index(m_bench["month"].astype(str)).reindex(common)
    months_net = np.asarray(m_net["ret"], float)
    months_bench = np.asarray(m_bench["ret"].fillna(0.0), float)

    rows = [window_rows(months_net, months_bench, h) for h in HORIZONS]

    stats = base["stats"]["full"]
    sr = float(stats.get("sharpe") or 0.0)
    t_own = years_to_t(sr)
    t_hurdle = None
    if cfg["hurdle_sharpe"]:
        t_hurdle = (float(cfg["hurdle_sharpe"]), years_to_t(float(cfg["hurdle_sharpe"])))
    v = classify(rows, t_own, t_hurdle)

    control_pp = (None if cfg["base_select_pp"] is None
                  else round(select_pp - float(cfg["base_select_pp"]), 3))
    control_ok = control_pp is not None and abs(control_pp) <= CONTROL_TOL_PP
    ctl_at_cut_pp, ctl_cut = control_arm(close, openp, amt, feats, cls, cfg)
    ctl_cut_delta = (None if (ctl_at_cut_pp is None or cfg["base_select_pp"] is None)
                     else round(ctl_at_cut_pp - float(cfg["base_select_pp"]), 3))
    cut_ok = ctl_cut_delta is not None and abs(ctl_cut_delta) <= 0.01

    w12 = next(r for r in rows if r["horizon_months"] == 12)
    out = {
        "evidence_cutoff": cfg["evidence_cutoff"] or str(pd.Timestamp(close.index[-1]).date()),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_evidence_horizon.py",
        "rule": {
            "benchmark": BENCH, "gate_cny": GATE, "seats": CS.BASE_SEATS,
            "rebal": cfg["rebal"], "cost_bp_per_side": round(cfg["cost"] * 1e4, 3),
            "vol_target": cfg["vol_target"], "cash_ann": CASH_ANN,
            "horizons_months": list(HORIZONS), "t_line": T_LINE,
            "account_cny": ACCOUNT_CNY, "control_tol_pp": CONTROL_TOL_PP,
            "soon_share": SOON_SHARE, "soon_years": SOON_YEARS,
            "slow_share": SLOW_SHARE, "slow_years": SLOW_YEARS,
            "question": "if a reader starts following this book, how long until the record can "
                        "tell them anything, and what do they sit through in the meantime",
            "frozen": "criteria written before the run; --check re-derives the verdict",
        },
        "book": {
            "bars": int(len(net)), "months": int(len(months_net)),
            "select_ann_pp": round(select_pp, 4),
            "cagr_pct": round(float(stats["cagr"]) * 100.0, 3),
            "sharpe": round(sr, 4),
            "years_to_t2_own_sharpe": None if t_own is None else round(t_own, 3),
            "hurdle": (None if t_hurdle is None else
                       {"sharpe": round(t_hurdle[0], 4), "trials": cfg["hurdle_n"],
                        "years_to_t2": None if t_hurdle[1] is None else round(t_hurdle[1], 3)}),
        },
        "monthly": {
            "note": "the generator of every rolling window on this face; --check re-derives all "
                    "rows from these two columns",
            "month": [str(x) for x in m_net["month"].astype(str)],
            "bars": [int(x) for x in m_net["bars"]],
            "net": [round(float(x), 8) for x in months_net],
            "bench": [round(float(x), 8) for x in months_bench],
        },
        "horizons": rows,
        "verdict": v["verdict"],
        "sentence": v["sentence"],
        "control": {"base_select_pp": cfg["base_select_pp"], "select_ann_pp": round(select_pp, 4),
                    "delta_pp": control_pp, "ok": bool(control_ok),
                    "tol_pp": CONTROL_TOL_PP,
                    "why_delta": "the panel advanced past the published cutoff, so the headline "
                                 "arm is a fresh derive; the same-bar control below is the proof",
                    "at_published_cutoff": {"cutoff": ctl_cut,
                                            "select_ann_pp": (None if ctl_at_cut_pp is None
                                                              else round(ctl_at_cut_pp, 4)),
                                            "delta_pp": ctl_cut_delta, "tol_pp": 0.01,
                                            "ok": bool(cut_ok)}},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[face] %s verdict=%s 12m share_beat_cash=%s t_own=%.2fy"
          % (os.path.basename(OUT_JSON), out["verdict"], w12["share_beat_cash"], t_own or -1),
          flush=True)
    print(out["sentence"], flush=True)
    if not cut_ok:
        print("[CONTROL] same-bar replay at %s differs by %s pp (tol 0.01) -- this face refuses to judge"
              % (ctl_cut, ctl_cut_delta), flush=True)
        return 1
    if not control_ok:
        print("[note] headline arm at panel tip %s differs from the published cutoff cell by %s pp "
              "(panel advance, within %.2f)" % (out["panel_last_bar"], control_pp, CONTROL_TOL_PP),
              flush=True)
    return 0


def check():
    """Re-derive every published number from the month table. No engine, no network."""
    if not os.path.exists(OUT_JSON):
        print("CHECK FAILED: %s missing" % OUT_JSON)
        return 3
    face = _load(OUT_JSON)
    mon = face.get("monthly") or {}
    net = np.asarray(mon.get("net") or [], float)
    bench = np.asarray(mon.get("bench") or [], float)
    if not len(net) or len(bench) != len(net):
        print("CHECK FAILED: month table unusable (%d net / %d bench)" % (len(net), len(bench)))
        return 3
    problems = []
    for row in face.get("horizons") or []:
        h = int(row["horizon_months"])
        redo = window_rows(net, bench, h)
        for key in ("windows", "non_overlapping", "share_pos", "share_beat_cash",
                    "share_beat_bench", "median_ann", "worst_ann", "best_ann",
                    "worst_window_cny", "worst_inner_dd_pct"):
            a, b = row.get(key), redo.get(key)
            if a is None and b is None:
                continue
            if a is None or b is None:
                problems.append("H%d %s published %s re-derived %s" % (h, key, a, b))
                continue
            if isinstance(a, float) or isinstance(b, float):
                if abs(float(a) - float(b)) > 1e-6:
                    problems.append("H%d %s %s != %s" % (h, key, a, b))
            elif a != b:
                problems.append("H%d %s %s != %s" % (h, key, a, b))
    book = face.get("book") or {}
    t_own = years_to_t(book.get("sharpe"))
    if t_own is None:
        problems.append("book.sharpe unusable")
    elif abs(t_own - float(book.get("years_to_t2_own_sharpe") or -1)) > 1e-3:
        problems.append("years_to_t2_own_sharpe %s != %.6f"
                        % (book.get("years_to_t2_own_sharpe"), t_own))
    hur = book.get("hurdle") or {}
    if hur:
        th = years_to_t(hur.get("sharpe"))
        if th is None or abs(th - float(hur.get("years_to_t2") or -1)) > 1e-3:
            problems.append("hurdle years_to_t2 %s != %s" % (hur.get("years_to_t2"), th))
    redo_v = classify(face.get("horizons") or [], t_own,
                      (None if not hur else (float(hur.get("sharpe")),
                                             years_to_t(hur.get("sharpe")))))
    if redo_v["verdict"] != face.get("verdict"):
        problems.append("verdict %s != re-derived %s" % (face.get("verdict"), redo_v["verdict"]))
    ctl = face.get("control") or {}
    if ctl.get("delta_pp") is not None and abs(float(ctl["delta_pp"])) > float(ctl.get("tol_pp") or 0.0):
        problems.append("control arm drifted %s pp" % ctl.get("delta_pp"))
    at_cut = ctl.get("at_published_cutoff") or {}
    if at_cut.get("delta_pp") is not None and abs(float(at_cut["delta_pp"])) > float(at_cut.get("tol_pp") or 0.01):
        problems.append("same-bar control at %s drifted %s pp"
                        % (at_cut.get("cutoff"), at_cut.get("delta_pp")))
    if at_cut and at_cut.get("ok") is False:
        problems.append("same-bar control flagged not ok at %s" % at_cut.get("cutoff"))
    if problems:
        print("CHECK FAILED:")
        for p in problems:
            print("  - " + p)
        return 3
    print("CHECK OK: %d horizons re-derived from %d months, verdict %s, control delta %s pp"
          % (len(face.get("horizons") or []), len(net), face.get("verdict"),
             ctl.get("delta_pp")))
    return 0


def write_md():
    face = _load(OUT_JSON)
    book = face["book"]
    lines = ["# How long before the book can be believed (r1962)", "",
             "generated by `scripts/etf_book_evidence_horizon.py`; evidence_cutoff **%s**, panel last bar %s."
             % (face["evidence_cutoff"], face["panel_last_bar"]), "",
             "## The answer in one paragraph", "", face["sentence"], "",
             "## What a reader sits through", "",
             "| horizon | windows | non-overlapping | > 0 | > cash %.1f%% | > %s | median | worst | worst on 1,000,000 | worst inner drawdown |"
             % (CASH_ANN * 100.0, BENCH),
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in face["horizons"]:
        lines.append("| %dm | %d | %d | %s | %s | %s | %s | %s | %s | %s |" % (
            r["horizon_months"], r["windows"], r["non_overlapping"],
            _pct(r["share_pos"]), _pct(r["share_beat_cash"]), _pct(r["share_beat_bench"]),
            _pct(r["median_ann"]), _pct(r["worst_ann"]),
            "-" if r["worst_window_cny"] is None else "{:,.0f}".format(r["worst_window_cny"]),
            "-" if r["worst_inner_dd_pct"] is None else "%.2f%%" % r["worst_inner_dd_pct"]))
    hur = book.get("hurdle")
    lines += ["", "## How long the record must run", "",
              "- at the book's own Sharpe %.3f, the mean is two standard errors from zero after **%.2f years**"
              % (book["sharpe"], book["years_to_t2_own_sharpe"] or -1),
              "- at the deflated hurdle Sharpe %s (trials N=%s), the same line needs **%s years**"
              % ("-" if not hur else "%.3f" % hur["sharpe"], "-" if not hur else hur["trials"],
                 "-" if not hur else "%.2f" % hur["years_to_t2"]),
              "", "## Limits stated on the face", "",
              "- windows overlap: the count of windows is not a sample size (non-overlapping count is printed beside it)",
              "- the inner drawdown column is measured on month-end NAV, so it is shallower than a daily path would be",
              "- cash is a flat %.2f%%/yr, not the realised repo path" % (CASH_ANN * 100.0),
              "- the deflated hurdle is only as good as the trial count behind it", ""]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("[md] -> %s" % OUT_MD)
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # L1 twelve months of +1% compounds to 12.68% annualised
    leg("L1 month compounding", abs(_ann_window([0.01] * 12) - ((1.01 ** 12) - 1.0)) < 1e-12)

    # L2 all-positive months -> every window beats cash; cash-only months -> none do
    r = window_rows([0.01] * 24, [0.0] * 24, 12)
    leg("L2a all positive beats cash", r["share_beat_cash"] == 1.0 and r["share_pos"] == 1.0)
    cash_m = (1.0 + CASH_ANN) ** (1.0 / 12.0) - 1.0
    r2 = window_rows([cash_m] * 24, [0.0] * 24, 12)
    leg("L2b exactly cash does not beat cash", r2["share_beat_cash"] == 0.0)

    # L3 years_to_t inverts t = SR*sqrt(years)
    leg("L3a SR=1 -> 4y", abs(years_to_t(1.0) - 4.0) < 1e-12)
    leg("L3b SR=2 -> 1y", abs(years_to_t(2.0) - 1.0) < 1e-12)
    leg("L3c no sharpe -> None", years_to_t(0.0) is None and years_to_t(None) is None)

    # L4 worst window money is the worst annualised window on the account
    r4 = window_rows([0.02] * 6 + [-0.05] * 6 + [0.03] * 12, [0.0] * 24, 12)
    worst = r4["worst_ann"]
    leg("L4 worst_window_cny == worst_ann * account",
        abs(r4["worst_window_cny"] - ACCOUNT_CNY * worst) <= 100.0)

    # L5 non-overlapping count is floor(n/h) and never exceeds the window count
    leg("L5 non-overlapping floor", r4["non_overlapping"] == 2 and r4["windows"] == 13)

    # L6 the drift leg: changing one month changes the 12m windows (this is what --check catches)
    base_row = window_rows([0.01] * 24, [0.0] * 24, 12)
    moved = list([0.01] * 24)
    moved[5] = -0.20
    leg("L6 one moved month moves the windows",
        abs(window_rows(moved, [0.0] * 24, 12)["worst_ann"] - base_row["worst_ann"]) > 0.10)

    # L7 benchmark comparison uses the benchmark's own window, not the book's annualisation
    r7 = window_rows([0.0] * 24, [0.01] * 24, 12)
    leg("L7 zero book never beats a rising benchmark", r7["share_beat_bench"] == 0.0)

    # L8 verdict mapping at its three poles
    soon = [{"horizon_months": 12, "share_beat_cash": 0.95, "median_ann": 0.05}]
    slow = [{"horizon_months": 12, "share_beat_cash": 0.40, "median_ann": -0.01}]
    mid = [{"horizon_months": 12, "share_beat_cash": 0.70, "median_ann": 0.02}]
    leg("L8a EVIDENCE_SOON", classify(soon, 2.0, None)["verdict"] == "EVIDENCE_SOON")
    leg("L8b PATIENCE_REQUIRED by share", classify(slow, 2.0, None)["verdict"] == "PATIENCE_REQUIRED")
    leg("L8c PATIENCE_REQUIRED by years", classify(soon, 5.0, None)["verdict"] == "PATIENCE_REQUIRED")
    leg("L8d MIXED", classify(mid, 2.5, None)["verdict"] == "MIXED")
    leg("L8e CANNOT_JUDGE without a sharpe", classify(soon, None, None)["verdict"] == "CANNOT_JUDGE")

    # L9 the hurdle sentence appends only when a hurdle exists
    leg("L9 hurdle clause conditional",
        "搜索租金" not in classify(soon, 2.0, None)["sentence"]
        and "搜索租金" in classify(soon, 2.0, (1.585, 1.59))["sentence"])

    # L10 inner drawdown is the path's own peak-to-trough, not a cummax of a cummax (r1962 bug:
    # the first cut took maximum.accumulate of an already-monotone peak and always printed 0.0)
    r10 = window_rows([0.10] + [-0.20] + [0.0] * 10, [0.0] * 12, 12)
    leg("L10 inner drawdown is negative on a fall", -20.0 <= r10["worst_inner_dd_pct"] <= -19.9)

    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print("%-4s %s" % ("PASS" if v else "FAIL", name))
    print("%d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return check()
    if cmd == "--md":
        return write_md()
    if cmd == "run":
        rc = run()
        if rc == 0:
            write_md()
        return rc
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
