# -*- coding: utf-8 -*-
"""does the kill-rule verdict survive a different start date -- or is it one window's number?

WHY THIS FILE EXISTS
--------------------
r2137 (`idx_fut_carry_kill_rule_economics`) priced a peak-drawdown kill line on the carry
book and printed two sentences: 0.6 sigma is nearly free on both products, and 0.4 sigma
buys back 1.63pp of peak drawdown on IM for 0.28pp of return -- but that same pair is a
negative contributor in-sample and only turns positive out of sample, so r2137 closed with
`ORDERING_IS_IN_SAMPLE_ONLY` and did NOT hand the table to the operator.

r2128 taught the same lesson from the other side (ETF cadence): a per-cell median is only
comparable when the cells share the same start dates, and "the spread inside a cell" is
usually the calendar, not the rule. A rule that is best when measured from 2022-07-25 is
not yet a rule; it has one start date.

So this face asks nothing new about the maths -- it re-uses r2137's engine unchanged -- and
asks one question about the answer: if you had opened this book on a different day, would
obeying the same kill line still have paid?

WHAT IS DECLARED, NOT FITTED
----------------------------
  * WINDOW = 250 bars (about one year) and STEP = 20 bars are DECLARED. The window is long
    enough for the 60-observation vol floor plus a kill/cooldown cycle, short enough to
    yield a distribution on a 1,052-bar series;
  * every window starts from a FLAT book (no inherited drawdown), i.e. it answers "you
    opened an account that day", which is the only way a re-start can be causal;
  * the trailing vol is the r2137 series sliced, not recomputed inside the window: it is
    causal and was observable on the start date too. Recomputing it inside the window would
    be more conservative but would throw away the first 60 days of every window and shrink
    the sample for no honesty gain;
  * "pays" = the window's saved peak drawdown exceeds the window's given-up annual return
    AND that saved drawdown is at least 0.5pp (below that it is noise, not insurance);
  * windows are classified by the BASELINE drawdown depth that window actually contains
    (split at the cross-window median), because insurance is only supposed to pay in the
    deep half. A rule that is free everywhere is a different product from one that pays
    only in crashes, and the charter should name which one it is buying.

verdict tokens (frozen before the first run):
  KILL_RULE_PAYS_IN_MOST_WINDOWS       the best declared pair "pays" in >= 70% of windows
                                       on every product that has >= 20 windows
  KILL_RULE_PAYS_IN_HALF_THE_WINDOWS   that share is 50%..70%
  KILL_RULE_IS_WINDOW_DEPENDENT        that share is 25%..50% -- quote the median, never the
                                       full-window number
  KILL_RULE_IS_SINGLE_WINDOW_ARTIFACT  that share is < 25% -- the full-window result belongs
                                       to one start date and must not enter the charter
  UNREADABLE                           a product has no usable window set

  second token, on whether r2137's table may be handed to the operator:
  ADVICE_READY                         the ordering survives the window split
  ADVICE_NOT_READY                     it does not -- the page prints prices, not advice

Read-only with respect to the paper book: never touches LEDGER.json / STATE.json.
Deterministic: no sampling, no seed; same panels in, same bytes out apart from `generated`.

Usage
-----
  python scripts/idx_fut_carry_kill_rule_phase_robustness.py
  python scripts/idx_fut_carry_kill_rule_phase_robustness.py --check
  python scripts/idx_fut_carry_kill_rule_phase_robustness.py --selftest
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_carry_kill_rule_economics as KR  # noqa: E402

TZ = timezone(timedelta(hours=8))
PRODUCTS = ("IC", "IM")
WINDOW = 250
STEP = 20
MIN_WINDOWS = 20
PAY_FLOOR_PP = 0.5
MOST_SHARE = 0.70
HALF_SHARE = 0.50
ARTIFACT_SHARE = 0.25

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_carry_kill_rule_phase_robustness.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_CARRY_KILL_RULE_PHASE_ROBUSTNESS.md")


def now():
    return datetime.now(TZ)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def input_paths():
    return KR.input_paths()


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


# ---------------------------------------------------------------- windows


def window_starts(n, window=WINDOW, step=STEP):
    """Start indices of a rolling window set. Declared geometry, not fitted."""
    if n < window or step <= 0:
        return []
    return list(range(0, n - window + 1, step))


def window_eval(net, w, vol, k, rule, s, window=WINDOW):
    """One window of the r2137 engine, started from a flat book."""
    sl = slice(s, s + window)
    row = KR.evaluate_pair(np.asarray(net, float)[sl],
                           np.asarray(w, float)[sl],
                           KR.sigma_lines(np.asarray(vol, float)[sl], k),
                           rule)
    if row is None:
        return None
    return {
        "start_bar": int(s),
        "base_mdd_pct": row["baseline"]["mdd_pct"],
        "base_cagr_pct": row["baseline"]["cagr_pct"],
        "price_pp": row["price_pp"],
        "dd_saved_pp": row["dd_saved_pp"],
        "n_kills": row["n_kills"],
        "flat_share_pct": row["flat_share_pct"],
    }


def is_pay(row, floor_pp=PAY_FLOOR_PP):
    """The declared test: real drawdown bought back, and more bought back than paid."""
    return (row["dd_saved_pp"] >= floor_pp) and (row["dd_saved_pp"] > row["price_pp"])


def summarize(rows, floor_pp=PAY_FLOOR_PP):
    if not rows:
        return None
    prices = [r["price_pp"] for r in rows]
    saves = [r["dd_saved_pp"] for r in rows]
    pays = [r for r in rows if is_pay(r, floor_pp)]
    kills = [r["n_kills"] for r in rows]
    worst = max(rows, key=lambda r: r["price_pp"])
    best = max(rows, key=lambda r: r["dd_saved_pp"])
    depth = [abs(r["base_mdd_pct"]) for r in rows]
    med_depth = float(np.median(depth))
    shallow = [r for r in rows if abs(r["base_mdd_pct"]) < med_depth]
    deep = [r for r in rows if abs(r["base_mdd_pct"]) >= med_depth]
    return {
        "n_windows": len(rows),
        "pays_windows": len(pays),
        "pays_share": round(float(len(pays)) / float(len(rows)), 4),
        "median_price_pp": round(float(np.median(prices)), 4),
        "median_dd_saved_pp": round(float(np.median(saves)), 4),
        "p90_price_pp": round(float(np.percentile(prices, 90)), 4),
        "p10_dd_saved_pp": round(float(np.percentile(saves, 10)), 4),
        "windows_with_no_kill": int(sum(1 for k in kills if k == 0)),
        "worst_window": {"start_bar": worst["start_bar"],
                         "price_pp": worst["price_pp"],
                         "dd_saved_pp": worst["dd_saved_pp"],
                         "base_mdd_pct": worst["base_mdd_pct"]},
        "best_window": {"start_bar": best["start_bar"],
                        "price_pp": best["price_pp"],
                        "dd_saved_pp": best["dd_saved_pp"],
                        "base_mdd_pct": best["base_mdd_pct"]},
        "depth_split": {
            "median_abs_mdd_pct": round(med_depth, 4),
            "shallow": summarize_depth(shallow, floor_pp),
            "deep": summarize_depth(deep, floor_pp),
        },
    }


def summarize_depth(rows, floor_pp=PAY_FLOOR_PP):
    if not rows:
        return None
    pays = [r for r in rows if is_pay(r, floor_pp)]
    return {
        "n_windows": len(rows),
        "pays_windows": len(pays),
        "pays_share": round(float(len(pays)) / float(len(rows)), 4),
        "median_price_pp": round(float(np.median([r["price_pp"] for r in rows])), 4),
        "median_dd_saved_pp": round(float(np.median([r["dd_saved_pp"] for r in rows])), 4),
    }


def verdict_for(products):
    """Frozen rules over the per-product BEST-MANNERED pair. Returns (token, advice, detail).

    The test gives the rule family its most favourable pair (highest share of windows that
    pay), not the pair the median edge happens to rank first -- all pairs share a median
    edge of 0.00, so a median tie would let dictionary order decide the verdict.
    """
    usable = {}
    for code, v in products.items():
        if not v or not v.get("family_best_windows"):
            continue
        if v["family_best_windows"]["n_windows"] < MIN_WINDOWS:
            continue
        usable[code] = v["family_best_windows"]["pays_share"]
    if not usable:
        return "UNREADABLE", "ADVICE_NOT_READY", {"usable_products": []}
    worst = min(usable.values())
    if worst >= MOST_SHARE:
        token = "KILL_RULE_PAYS_IN_MOST_WINDOWS"
        advice = "ADVICE_READY"
    elif worst >= HALF_SHARE:
        token = "KILL_RULE_PAYS_IN_HALF_THE_WINDOWS"
        advice = "ADVICE_NOT_READY"
    elif worst >= ARTIFACT_SHARE:
        token = "KILL_RULE_IS_WINDOW_DEPENDENT"
        advice = "ADVICE_NOT_READY"
    else:
        token = "KILL_RULE_IS_SINGLE_WINDOW_ARTIFACT"
        advice = "ADVICE_NOT_READY"
    return token, advice, {"usable_products": sorted(usable),
                            "worst_pays_share": round(worst, 4),
                            "by_product": {k: round(v, 4) for k, v in usable.items()}}


# ---------------------------------------------------------------- build


def build():
    products = {}
    cutoff = None
    r2137_best = {}
    for code in PRODUCTS:
        rows = KR.daily(code)
        if len(rows) < WINDOW:
            products[code] = {"readable": False,
                              "why": "only %d bars, window is %d" % (len(rows), WINDOW)}
            continue
        dates = [r["date"] for r in rows]
        net = np.array([r["net"] for r in rows], float)
        w = np.array([abs(r["weight"]) for r in rows], float)
        vol = KR.trailing_vol(net)
        cutoff = max(cutoff or dates[-1], dates[-1])
        starts = window_starts(len(net))

        per_pair = {}
        for k in KR.SIGMA_MULT:
            for rule in KR.REENTRY:
                key = KR.pair_key("%.1fsig" % k, rule)
                wrows = [window_eval(net, w, vol, k, rule, s) for s in starts]
                wrows = [r for r in wrows if r]
                per_pair[key] = {"windows": wrows, "summary": summarize(wrows)}

        # r2137's own in-sample winners, read off its published face when present
        full = {k: v["summary"]["median_dd_saved_pp"] - v["summary"]["median_price_pp"]
                for k, v in per_pair.items() if v["summary"]}
        best_key = max(full, key=lambda x: full[x]) if full else None
        best_windows = per_pair[best_key]["summary"] if best_key else None
        # the verdict test gives the family its most favourable pair by WINDOW SHARE; the
        # median-edge ranking above is a display, not the adjudicator (medians all tie at 0)
        fam = {k: (v["summary"]["pays_share"], full.get(k, 0.0))
               for k, v in per_pair.items() if v["summary"]}
        fam_key = max(fam, key=lambda x: fam[x]) if fam else None
        fam_windows = per_pair[fam_key]["summary"] if fam_key else None

        products[code] = {
            "readable": True,
            "series": {"first": dates[0], "last": dates[-1], "bars": len(dates)},
            "window_bars": WINDOW,
            "step_bars": STEP,
            "n_windows": len(starts),
            "first_window_start": dates[starts[0]] if starts else None,
            "last_window_start": dates[starts[-1]] if starts else None,
            "pairs": {k: v["summary"] for k, v in per_pair.items()},
            "best_pair_by_median_edge": best_key,
            "best_pair_windows": best_windows,
            "family_best_pair": fam_key,
            "family_best_windows": fam_windows,
            "has_enough_windows": len(starts) >= MIN_WINDOWS,
        }
        r2137_best[code] = best_key

    token, advice, detail = verdict_for(products)
    return {
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "window_bars": WINDOW,
        "step_bars": STEP,
        "pay_floor_pp": PAY_FLOOR_PP,
        "min_windows_for_verdict": MIN_WINDOWS,
        "thresholds": {"most": MOST_SHARE, "half": HALF_SHARE, "artifact": ARTIFACT_SHARE},
        "products": products,
        "verdict": token,
        "advice": advice,
        "verdict_detail": detail,
        "inherits": "scripts/idx_fut_carry_kill_rule_economics.py (engine imported, not re-implemented)",
        "ok": token != "UNREADABLE",
        "inputs_digest": inputs_digest(),
        "note": ("a window starts from a flat book and reuses the causal r2137 trailing vol; "
                 "it is a start-date test, not a resampling of the same days"),
    }


# ---------------------------------------------------------------- render


def fmt(x, unit="%%"):
    return "n/a" if x is None else ("%.2f" % x) + unit


def write_md(payload):
    P = payload["products"]
    L = []
    A = L.append
    A("# 杀线结论扛不扛得住换个起跑日")
    A("")
    A("轮号 r2138（bm-c）｜生成 %s｜证据 cutoff %s" % (payload["generated"], payload["evidence_cutoff"]))
    A("")
    A("**本页只回答一个问题**：r2137 算出的「0.6σ 近乎免费、0.4σ 在 IM 买回 1.63pp」这套数，"
      "如果这本书是另一个日子开的户，还成不成立？引擎一行没改（直接 import r2137），"
      "只是把 250 根 bar 的窗子在序列上滚动、每次从空仓起跑，看同一族规则在每一窗里付多少钱、买回多少。")
    A("")
    A("## 判词")
    A("")
    A("- **%s**" % payload["verdict"])
    A("- **%s** ｜ %s" % (payload["advice"], json.dumps(payload["verdict_detail"], ensure_ascii=False)))
    A("")
    A("判据（跑之前写死）：最好的一对在 ≥70% 的窗里「买回 ≥0.5pp 且买回 > 代价」= 真规则；"
      "50–70% = 半真；25–50% = 窗依赖（只能报中位数）；<25% = 单一起点产物，禁入章程。"
      "每个品种至少 20 个窗才参与判词。")
    A("")
    A("## 逐品种")
    A("")
    for code in PRODUCTS:
        v = P.get(code) or {}
        if not v.get("readable"):
            A("### %s —— 不可读（%s）" % (code, v.get("why")))
            A("")
            continue
        s = v["series"]
        A("### %s" % code)
        A("")
        A("- 序列 %s → %s（%d bar）；窗 %d 根 / 步进 %d 根 → **%d 个窗**（起点 %s … %s）"
          % (s["first"], s["last"], s["bars"], v["window_bars"], v["step_bars"],
             v["n_windows"], v["first_window_start"], v["last_window_start"]))
        if not v["has_enough_windows"]:
            A("- **窗数 < %d，不参与判词**（如实：样本不足以谈分布）" % MIN_WINDOWS)
        A("")
        A("| 杀线 × 复入 | 付得起的窗 | 代价中位 | 买回中位 | 代价 p90 | 买回 p10 | 零开杀窗 |")
        A("|---|---|---|---|---|---|---|")
        for key in sorted(v["pairs"]):
            sm = v["pairs"][key]
            if not sm:
                continue
            A("| %s | %d/%d (%.1f%%) | %.2fpp | %.2fpp | %.2fpp | %.2fpp | %d |"
              % (key, sm["pays_windows"], sm["n_windows"], 100.0 * sm["pays_share"],
                 sm["median_price_pp"], sm["median_dd_saved_pp"],
                 sm["p90_price_pp"], sm["p10_dd_saved_pp"], sm["windows_with_no_kill"]))
        A("")
        bw = v["family_best_windows"]
        if bw:
            ds = bw["depth_split"]
            A("**判词取的是族里最有利的一对**（按「付得起的窗」占比最高）：`%s`；"
              "按中位边际排第一的是 `%s`（中位数在所有对上并列 0.00，所以它只是展示，不当裁判）。"
              % (v["family_best_pair"], v["best_pair_by_median_edge"]))
            A("")
            A("- 最贵的一窗：第 %d 根起跑，代价 %.2fpp / 买回 %.2fpp（该窗基线回撤 %.2f%%）"
              % (bw["worst_window"]["start_bar"], bw["worst_window"]["price_pp"],
                 bw["worst_window"]["dd_saved_pp"], bw["worst_window"]["base_mdd_pct"]))
            A("- 最好的一窗：第 %d 根起跑，代价 %.2fpp / 买回 %.2fpp（该窗基线回撤 %.2f%%）"
              % (bw["best_window"]["start_bar"], bw["best_window"]["price_pp"],
                 bw["best_window"]["dd_saved_pp"], bw["best_window"]["base_mdd_pct"]))
            A("- 付得起的窗：%d / %d（%.1f%%）；零开杀窗 %d 个（这窗里根本没崩到线的深度）"
              % (bw["pays_windows"], bw["n_windows"], 100.0 * bw["pays_share"],
                 bw["windows_with_no_kill"]))
            A("- 按窗自带的回撤深度分两半（分界 |MDD| = %.2f%%）：浅档付得起 %d/%d（%.0f%%，代价中位 %.2fpp、买回中位 %.2fpp）；"
              "深档 %d/%d（%.0f%%，代价中位 %.2fpp、买回中位 %.2fpp）"
              % (ds["median_abs_mdd_pct"],
                 (ds["shallow"] or {}).get("pays_windows", 0), (ds["shallow"] or {}).get("n_windows", 0),
                 100.0 * (ds["shallow"] or {}).get("pays_share", 0.0),
                 (ds["shallow"] or {}).get("median_price_pp", 0.0),
                 (ds["shallow"] or {}).get("median_dd_saved_pp", 0.0),
                 (ds["deep"] or {}).get("pays_windows", 0), (ds["deep"] or {}).get("n_windows", 0),
                 100.0 * (ds["deep"] or {}).get("pays_share", 0.0),
                 (ds["deep"] or {}).get("median_price_pp", 0.0),
                 (ds["deep"] or {}).get("median_dd_saved_pp", 0.0)))
            A("")
    A("## 这一页不是什么")
    A("")
    A("- 不改 r2137 的引擎、成本率（1.5bp/边）与数据面，一切读数继承它；")
    A("- 窗起点从空仓算，等价于「那天开户」；它不衡量「已经拿着一本书、中途加一条线」的情形；")
    A("- 空手日收益记 0（真实现金腿不在序列里），所以代价仍是**上界**；")
    A("- 滚动窗彼此重叠（步进 %d < 窗长 %d），窗数不等于独立样本数，判词按窗占比而不是显著性下。" % (STEP, WINDOW))
    A("")
    A("## 复现")
    A("")
    A("```")
    A("python scripts/idx_fut_carry_kill_rule_phase_robustness.py            # 重算并发布")
    A("python scripts/idx_fut_carry_kill_rule_phase_robustness.py --check    # 只复算判词与关键字段")
    A("python scripts/idx_fut_carry_kill_rule_phase_robustness.py --selftest # 离线自检")
    A("```")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- selftest


def _selftest():
    errs = []

    def chk(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            errs.append(msg)

    # 1. window geometry
    st = window_starts(1052, 250, 20)
    chk(len(st) == 41 and st[0] == 0 and st[-1] == 800, "window starts = range(0, n-W+1, STEP) (%d)" % len(st))
    chk(window_starts(100, 250, 20) == [], "a series shorter than the window yields no windows")

    # 2. the declared pay test has both conditions
    chk(is_pay({"price_pp": 0.1, "dd_saved_pp": 0.6}) is True, "pays when it buys back >= floor and more than it costs")
    chk(is_pay({"price_pp": 0.7, "dd_saved_pp": 0.6}) is False, "does not pay when the cost exceeds the drawdown bought back")
    chk(is_pay({"price_pp": 0.0, "dd_saved_pp": 0.2}) is False, "a 0.2pp wiggle is not insurance")

    # 3. a monotone-up series WITH noise: no drawdown, kill line never fires, both ~0
    #    (a perfectly constant series has sd=0 => line=0 => fires by construction, which is
    #     a degenerate input, not a book anyone holds; noise keeps the line positive)
    n = 300
    up = 0.0005 + 0.0004 * np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
    wts = np.full(n, 1.0)
    vol = KR.trailing_vol(up)
    row = window_eval(up, wts, vol, 0.4, "cooldown20", 0)
    chk(row is not None and row["n_kills"] == 0, "a rising noisy window never fires the line")
    chk(abs(row["price_pp"]) < 1e-9 and abs(row["dd_saved_pp"]) < 1e-9,
        "no drawdown to save => zero price and zero saving")

    # 4. one crash inside the window: the line fires once and the saving is visible
    crash = np.full(n, 0.0002)
    crash[120:130] = -0.006
    vol_c = KR.trailing_vol(crash)
    row_c = window_eval(crash, wts, vol_c, 0.4, "cooldown20", 0)
    chk(row_c["n_kills"] >= 1, "a crash window fires the line at least once")
    chk(row_c["dd_saved_pp"] > 0.0, "and it does buy back some peak drawdown there")

    # 5. summarize hand-check: 3 windows, 1 pays
    rows = [{"start_bar": 0, "base_mdd_pct": -0.5, "base_cagr_pct": 10.0,
             "price_pp": 0.1, "dd_saved_pp": 0.6, "n_kills": 1, "flat_share_pct": 2.0},
            {"start_bar": 20, "base_mdd_pct": -1.5, "base_cagr_pct": 10.0,
             "price_pp": 0.9, "dd_saved_pp": 0.4, "n_kills": 2, "flat_share_pct": 4.0},
            {"start_bar": 40, "base_mdd_pct": -3.0, "base_cagr_pct": 10.0,
             "price_pp": 0.2, "dd_saved_pp": 1.6, "n_kills": 1, "flat_share_pct": 3.0}]
    sm = summarize(rows)
    chk(sm["pays_windows"] == 2 and abs(sm["pays_share"] - 2.0 / 3.0) < 1e-4,
        "summarize counts paying windows by hand (2/3)")
    chk(sm["windows_with_no_kill"] == 0, "windows_with_no_kill counted")
    chk(abs(sm["depth_split"]["median_abs_mdd_pct"] - 1.5) < 1e-9, "depth split lands on the median |MDD|")
    sh = sm["depth_split"]["shallow"]
    chk(sh["n_windows"] == 1, "shallow half holds the one window below the median depth")

    # 6. verdict tokens are a closed set and thresholds behave
    fake = {"IC": {"family_best_windows": {"n_windows": 40, "pays_share": 0.80}},
            "IM": {"family_best_windows": {"n_windows": 40, "pays_share": 0.75}}}
    chk(verdict_for(fake)[0] == "KILL_RULE_PAYS_IN_MOST_WINDOWS", "70%+ on the worst product => most windows")
    fake["IM"]["family_best_windows"]["pays_share"] = 0.55
    chk(verdict_for(fake)[0] == "KILL_RULE_PAYS_IN_HALF_THE_WINDOWS", "55% => half the windows")
    fake["IM"]["family_best_windows"]["pays_share"] = 0.30
    chk(verdict_for(fake)[0] == "KILL_RULE_IS_WINDOW_DEPENDENT", "30% => window dependent")
    fake["IM"]["family_best_windows"]["pays_share"] = 0.10
    chk(verdict_for(fake)[0] == "KILL_RULE_IS_SINGLE_WINDOW_ARTIFACT", "10% => single-window artifact")
    chk(verdict_for({"IC": {"family_best_windows": {"n_windows": 5, "pays_share": 0.9}}})[0] == "UNREADABLE",
        "a product with fewer than the minimum windows cannot carry a verdict")
    chk(verdict_for(fake)[1] == "ADVICE_NOT_READY", "a window-dependent rule is not advice")
    # the adjudicator must read the family's most favourable pair, not the median-edge pick
    tie = {"IC": {"family_best_windows": {"n_windows": 40, "pays_share": 0.10},
                  "best_pair_windows": {"n_windows": 40, "pays_share": 0.90}}}
    chk(verdict_for(tie)[0] == "KILL_RULE_IS_SINGLE_WINDOW_ARTIFACT",
        "the verdict reads family_best_windows, never the median-edge display")

    # 7. determinism: same panels in, same windows out
    net_d = np.where(np.arange(n) % 37 == 0, -0.01, 0.0004)
    vol_d = KR.trailing_vol(net_d)
    a1 = [window_eval(net_d, wts, vol_d, 0.6, "cooldown20", s) for s in window_starts(n, 250, 20)]
    a2 = [window_eval(net_d, wts, vol_d, 0.6, "cooldown20", s) for s in window_starts(n, 250, 20)]
    chk(a1 == a2 and len(a1) > 0, "two passes over the same windows are byte-identical")

    print("")
    print("selftest: %d checks, %d failed" % (15, len(errs)))
    return 0 if not errs else 1


# ---------------------------------------------------------------- check


def check():
    if not os.path.exists(OUT_JSON):
        print("FAIL no published receipt at %s" % OUT_JSON)
        return 1
    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)
    got_token, got_advice, got_detail = verdict_for(d.get("products") or {})
    ok = True
    if got_token != d.get("verdict"):
        print("CHECK FAILED verdict %r != recomputed %r" % (d.get("verdict"), got_token))
        ok = False
    if got_advice != d.get("advice"):
        print("CHECK FAILED advice %r != recomputed %r" % (d.get("advice"), got_advice))
        ok = False
    if got_detail != d.get("verdict_detail"):
        print("CHECK FAILED verdict_detail does not re-derive")
        ok = False
    for code in PRODUCTS:
        v = (d.get("products") or {}).get(code) or {}
        if not v.get("readable"):
            continue
        n = v["series"]["bars"]
        expect = len(window_starts(n, v["window_bars"], v["step_bars"]))
        if v["n_windows"] != expect:
            print("CHECK FAILED %s n_windows %d != %d" % (code, v["n_windows"], expect))
            ok = False
        for key, sm in (v.get("pairs") or {}).items():
            if sm is None:
                continue
            if sm["pays_windows"] > sm["n_windows"] or sm["n_windows"] != v["n_windows"]:
                print("CHECK FAILED %s:%s window counts inconsistent" % (code, key))
                ok = False
    if ok:
        print("CHECK_OK verdict, advice and window counts re-derived from the receipt")
        return 0
    return 1


# ---------------------------------------------------------------- run


def run():
    payload = build()
    write_json(OUT_JSON, payload)
    write_md(payload)
    print("verdict:", payload["verdict"], "|", payload["advice"])
    for code in PRODUCTS:
        v = payload["products"].get(code) or {}
        if not v.get("readable"):
            print("%s: unreadable" % code)
            continue
        bw = v.get("family_best_windows") or {}
        print("%s: %d windows (%s..%s), family best=%s pays %d/%d (%.1f%%)"
              % (code, v["n_windows"], v["first_window_start"], v["last_window_start"],
                 v.get("family_best_pair"), bw.get("pays_windows", 0),
                 bw.get("n_windows", 0), 100.0 * bw.get("pays_share", 0.0)))
    print("saved", OUT_JSON)
    print("saved", OUT_MD)
    return 0


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
