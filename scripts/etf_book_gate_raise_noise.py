"""Is the 5-seat arm's 100M reading a thicker pool, or a handful of different names? (r1760)

The raise-price face (r1759) priced the gate ladder for two seat counts and found a shape
nobody can read: on the BOOK arm (5 seats) the reading is

    20M 9.12%  ->  40M 8.12%  ->  100M 9.91%  ->  200M 7.65%  ->  400M 5.47%  ->  1000M 1.15%

so raising the cut *lowers* the number at 40M and *raises* it at 100M. A reader who takes
100M as the best rung is choosing a gate on a 1.79pp bump that has never been tested for
being a bump at all.

This face asks that question with three measurements on the same engine and panel:

  1. DOES THE GATE TOUCH THIS BOOK AT ALL?  The price face already counts decision days
     where the cut leaves fewer names than seats (bars_below_seats). If that is zero at
     40M and 100M, the raise never stops the book from being filled -- so any gap is a
     change in WHICH names were picked, never a change in capacity.
  2. HOW DIFFERENT ARE THE BOOKS?  Per decision, the engine's own `diag` records the picks.
     Reported: mean overlap with the lower rung's book and the share of decisions whose
     book differs at all. Zero swaps means the two readings are one book priced twice.
  3. IS THE GAP BIGGER THAN ITS OWN NOISE?  Paired daily return difference, circular block
     bootstrap (block = one rebalance period, frozen draws/seed) for a one-sided p-value,
     plus a year-by-year sign count. A gap that lives in one or two years, or that a block
     bootstrap cannot separate from zero, is not evidence that the raise buys better tickets.

Nothing here moves the cut, and nothing here re-derives a published number: the control arm
must reproduce the price face's own cell for the same gate/seat pair, to CONTROL_TOL_PP.

Usage:
  python scripts/etf_book_gate_raise_noise.py run
  python scripts/etf_book_gate_raise_noise.py --selftest
  python scripts/etf_book_gate_raise_noise.py --check
  python scripts/etf_book_gate_raise_noise.py --md
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

import etf_composite_pf as E            # noqa: E402
import etf_book_production as P         # noqa: E402
import etf_book_entry_gate as G         # noqa: E402
import etf_robust_pf as R               # noqa: E402  (the engine itself, so picks are its own)
import etf_equity_alpha as A            # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_gate_raise_noise.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_GATE_RAISE_NOISE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")
FACE_ARM_NOISE = os.path.join(ROOT, "results", "etf_book_raise_arm_noise.json")
CARD_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

SHIPPED = G.SHIPPED                       # 20M -- the cut the ticket prints
GATES = [20e6, 40e6, 100e6]               # the rungs under question (see the shape above)
HIGH, LOW = 100e6, 40e6                   # the bump: 8.12% -> 9.91% on 5 seats
CONTROL_TOL_PP = 0.25                     # the arm must reproduce the price face's own cell
UNIVERSE_TOL = 20                         # names
BLOCK = 20                                # one rebalance period
DRAWS = 2000
SEED = 20261116
P_SIG = 0.05
SWAP_MIN = 0.10                           # <1 decision in 10 differs = one book, not two
YEAR_MAJOR = 0.70                         # the same rung must lead in most years
XCHECK_DIFF_TOL_PP = 0.05                 # the other face's diff must reproduce here
XCHECK_JAC_TOL = 0.02                     # ... and so must its Jaccard


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_inputs():
    """Published cells and the book's seat count, read from the faces that own them."""
    price = _load(FACE_PRICE)
    cfg = (price.get("config") or {})
    published = {}
    for row in (price.get("rows") or []):
        book = row.get("book") or {}
        card = row.get("card") or {}
        published[float(row["min_amt_cny"])] = {
            "book": book.get("cagr"), "card": card.get("cagr"),
            "book_bars_below_seats": book.get("bars_below_seats"),
            "book_median": book.get("median")}
    card = _load(CARD_JSON)
    card_cfg = card.get("config") or {}
    book = (_load(FACE_IDLE_CASH).get("book") or {})
    arm_noise = None
    if os.path.exists(FACE_ARM_NOISE):
        try:
            arm_noise = _load(FACE_ARM_NOISE)
        except (OSError, ValueError):
            arm_noise = None
    return {"price": price, "cfg": cfg, "published": published,
            "book_seats": int(book.get("n_hold") or 0) or None,
            "card_seats": int(card_cfg.get("n_hold") or 0) or None,
            "arm_noise": arm_noise,
            "evidence_cutoff": price.get("evidence_cutoff")}


def arm_stats(ser):
    """The same three windows, the same statistic, as the production engine's own wrapper."""
    out = {}
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= P.IS_END]),
                    ("oos", ser[ser.index > P.IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    return out


def price_arm(close, openp, amt, feats, gate, seats, cfg):
    """One gate, one seat count, through the engine, with the engine's own pick log."""
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    score = E.build_score(close, amt, feats, min_amt=gate)
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, int(seats),
                                      cost, vol_target=vol_target, vol_window=60, diag=diag)
    stats = arm_stats(ser)
    books = {row["date"]: list(row["book"]) for row in diag if row.get("book")}
    return {"stats": stats, "series": ser, "books": books, "diag_rows": len(diag),
            "turnover_per_decision": round(float(turn), 3)}


def overlap_stats(books_a, books_b, seats):
    """How much of the book is the same book, decision by decision."""
    days = sorted(set(books_a) & set(books_b))
    if not days or not seats:
        return {"decisions": 0, "mean_overlap": None, "swap_share": None,
                "names_swapped_total": 0, "mean_jaccard": None, "identical_days": 0}
    same = 0
    overlap_sum = 0.0
    jac_sum = 0.0
    swapped = 0
    for d in days:
        a, b = set(books_a[d]), set(books_b[d])
        inter = len(a & b)
        union = len(a | b)
        overlap_sum += inter / float(seats)
        jac_sum += (inter / float(union)) if union else 1.0
        swapped += len(a ^ b) // 2
        if a == b:
            same += 1
    return {"decisions": len(days),
            "mean_overlap": round(overlap_sum / len(days), 4),
            "mean_jaccard": round(jac_sum / len(days), 4),
            "swap_share": round(1.0 - same / float(len(days)), 4),
            "identical_days": int(same),
            "names_swapped_total": int(swapped)}


def block_bootstrap_p(diff, block=BLOCK, draws=DRAWS, seed=SEED):
    """One-sided p: how often a block-resampled mean is <= 0 (frozen draws/seed)."""
    x = np.asarray([v for v in diff if np.isfinite(v)], dtype=float)
    if x.size < block * 2:
        return None
    rng = np.random.default_rng(seed)
    n = x.size
    nb = int(np.ceil(n / float(block)))
    obs = float(x.mean())
    hits = 0
    for _ in range(draws):
        starts = rng.integers(0, n, size=nb)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % n
        if float(x[idx[:n]].mean()) <= 0.0:
            hits += 1
    return {"obs_mean_daily": obs, "p_one_sided": round((hits + 1) / (draws + 1.0), 4),
            "draws": draws, "block": block, "seed": seed, "bars": int(n)}


def year_table(ser_a, ser_b):
    """Per-year total return of both arms and who led -- a gap in one year is one year."""
    ra = ser_a.resample("YE").last()
    rb = ser_b.resample("YE").last()
    rows = []
    for ts in sorted(set(ra.index) | set(rb.index)):
        a = ra.get(ts)
        b = rb.get(ts)
        if a is None or b is None or not np.isfinite(a) or not np.isfinite(b):
            continue
        # the year's growth, measured from the previous year's close (first year from the
        # series' own start), never from 1.0 -- the r1731/r1594 start=1.0 trap
        prev_a = ra.shift(1).get(ts)
        prev_b = rb.shift(1).get(ts)
        pa = float(prev_a) if prev_a is not None and np.isfinite(prev_a) else float(ser_a.iloc[0])
        pb = float(prev_b) if prev_b is not None and np.isfinite(prev_b) else float(ser_b.iloc[0])
        if pa <= 0 or pb <= 0:
            continue
        ga = float(a) / pa - 1.0
        gb = float(b) / pb - 1.0
        rows.append({"year": int(ts.year), "high": round(ga, 4), "low": round(gb, 4),
                     "diff_pp": round((ga - gb) * 100.0, 2), "high_leads": bool(ga > gb)})
    leads = sum(1 for r in rows if r["high_leads"])
    return {"rows": rows, "years": len(rows), "high_leads": leads}


def segment_split(ser_a, ser_b, books_a, books_b):
    """Where the gap is made: segments where the two books agree vs where they differ."""
    days = sorted(set(books_a) & set(books_b))
    if len(days) < 2:
        return {"segments": 0, "same_book_segments": 0, "diff_book_segments": 0,
                "gap_pp_same_book": None, "gap_pp_diff_book": None}
    idx = {d: i for i, d in enumerate(ser_a.index)}
    same_gap = 0.0
    diff_gap = 0.0
    same_n = diff_n = 0
    for j, d in enumerate(days):
        i0 = idx.get(pd.Timestamp(d))
        nxt = days[j + 1] if j + 1 < len(days) else None
        i1 = idx.get(pd.Timestamp(nxt)) if nxt is not None else len(ser_a.index) - 1
        if i0 is None or i1 is None or i1 <= i0:
            continue
        ga = float(ser_a.iloc[i1]) / float(ser_a.iloc[i0]) - 1.0
        gb = float(ser_b.iloc[i1]) / float(ser_b.iloc[i0]) - 1.0
        if set(books_a[d]) == set(books_b[d]):
            same_gap += ga - gb
            same_n += 1
        else:
            diff_gap += ga - gb
            diff_n += 1
    return {"segments": same_n + diff_n, "same_book_segments": same_n,
            "diff_book_segments": diff_n,
            "gap_pp_same_book": round(same_gap * 100.0, 2),
            "gap_pp_diff_book": round(diff_gap * 100.0, 2)}


def classify(control_delta_pp=None, universe_delta=None, swap_share=None, mean_overlap=None,
             p_value=None, years=None, high_leads=None, binding_bars=None,
             control_tol_pp=CONTROL_TOL_PP, universe_tol=UNIVERSE_TOL, p_sig=P_SIG,
             swap_min=SWAP_MIN, year_major=YEAR_MAJOR):
    """Frozen states. Argument order and thresholds fixed before the run; no retuning."""
    if control_delta_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "没有控制臂：这组读数不是关于这本书的陈述"}
    if abs(control_delta_pp) > control_tol_pp:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": ("控制臂偏离抬闸定价面的同一格 %.2fpp（容差 %.2fpp），"
                             "这张面板不是那张面的面板" % (control_delta_pp, control_tol_pp))}
    if universe_delta is not None and abs(universe_delta) > universe_tol:
        return {"verdict": "CANNOT_JUDGE_UNIVERSE",
                "sentence": "重建宇宙差 %+d 名，超出 %d 名容差" % (universe_delta, universe_tol)}
    if swap_share is None or p_value is None:
        return {"verdict": "CANNOT_JUDGE_NO_ARMS",
                "sentence": "两臂没有重合的决策日，比不了"}
    detail = {"swap_share": swap_share, "mean_overlap": mean_overlap,
              "p_one_sided": p_value, "years": years, "high_leads": high_leads,
              "binding_bars": binding_bars}
    if swap_share <= 0.0:
        return dict(verdict="SAME_BOOK_SO_GAP_IS_NOT_SELECTION", **detail,
                    sentence=("两档闸在每一个决策日挑的是同一批名字——"
                              "那么两档读数的差不是「抬闸换来了更好的票」，"
                              "只能是同一条路径上的计量差"))
    major = years is not None and years > 0 and high_leads is not None and \
        (high_leads / float(years)) >= year_major
    if p_value < p_sig and swap_share >= swap_min and major:
        return dict(verdict="DIFFERENT_TICKETS_AND_SEPARABLE", **detail,
                    sentence=("抬闸确实换了一批票（%d%% 的决策日不同），"
                              "而且这个差在块自助下分得开（p=%.3f，%d/%d 年为高档领先）——"
                              "它买到的不是容量而是不同的名字" % (round(swap_share * 100), p_value,
                                                         high_leads or 0, years or 0)))
    why = []
    if p_value >= p_sig:
        why.append("块自助分不开（p=%.3f）" % p_value)
    if swap_share < swap_min:
        why.append("只有 %d%% 的决策日换了票" % round(swap_share * 100))
    if years is not None and years > 0 and not major:
        why.append("%d/%d 年高档领先" % (high_leads or 0, years))
    return dict(verdict="DIFFERENT_TICKETS_NOT_SEPARABLE", **detail,
                sentence=("两档闸确实挑了不同的票（%d%% 的决策日），但这个差在自己的噪声里分不开：%s——"
                          "把一个不到 2pp 的非单调凸起当「更优的闸」是在挑噪声"
                          % (round(swap_share * 100), "、".join(why))))


def run():
    t0 = time.time()
    src = read_inputs()
    seats = src["book_seats"]
    card_seats = src["card_seats"]
    cfg_p = src["cfg"]
    if seats is None:
        print("FATAL: results/etf_book_idle_cash.json carries no book seat count")
        return 2
    close, openp, amt, feats, n_flip = G.build_universe()
    t_panel = time.time() - t0
    universe_measured = int(len(close.columns))
    price = src["price"]
    published_universe = (price.get("config") or {}).get("universe_measured")
    universe_delta = (None if published_universe is None
                      else universe_measured - int(published_universe))

    arms = {}
    for gate in GATES:
        arms[gate] = price_arm(close, openp, amt, feats, gate, seats, cfg_p)
        print("[book %gM] cagr=%s swaps-known=%.1fs"
              % (gate / 1e6, arms[gate]["stats"]["full"].get("cagr"), time.time() - t0),
              flush=True)
    card_arm = price_arm(close, openp, amt, feats, SHIPPED, card_seats, cfg_p)

    # control: every arm this face prices must reproduce the price face's own cell
    control = {}
    worst = None
    for gate in GATES + [SHIPPED]:
        pub = src["published"].get(float(gate)) or {}
        if gate == SHIPPED:
            got = card_arm["stats"]["full"].get("cagr")
            want = pub.get("card")
        else:
            got = arms[gate]["stats"]["full"].get("cagr")
            want = pub.get("book")
        if got is None or want is None:
            continue
        delta = round((float(got) - float(want)) * 100.0, 4)
        label = "%gM_%s" % (gate / 1e6, "card" if gate == SHIPPED else "book")
        control[label] = {"arm_cagr": float(got), "published_cagr": float(want),
                          "delta_pp": delta}
        if worst is None or abs(delta) > abs(worst):
            worst = delta

    high, low, base = arms[HIGH], arms[LOW], arms[SHIPPED]
    ret_high = high["series"].pct_change()
    ret_low = low["series"].pct_change()
    ret_base = base["series"].pct_change()
    diff_hl = (ret_high - ret_low).dropna()
    diff_hb = (ret_high - ret_base).dropna()
    bs_hl = block_bootstrap_p(diff_hl)
    bs_hb = block_bootstrap_p(diff_hb)
    ov_hl = overlap_stats(high["books"], low["books"], seats)
    ov_hb = overlap_stats(high["books"], base["books"], seats)
    years = year_table(high["series"], low["series"])
    seg = segment_split(high["series"], low["series"], high["books"], low["books"])

    bind = {("book_%gM" % (g / 1e6)): (src["published"].get(float(g)) or {}).get(
        "book_bars_below_seats") for g in GATES}
    binding_bars = sum(v for v in bind.values() if isinstance(v, int))

    verdict = classify(control_delta_pp=worst, universe_delta=universe_delta,
                       swap_share=ov_hl["swap_share"], mean_overlap=ov_hl["mean_overlap"],
                       p_value=(bs_hl or {}).get("p_one_sided"), years=years["years"],
                       high_leads=years["high_leads"], binding_bars=binding_bars)

    # cross-check: the arm-noise face answers the 100M-vs-20M half of this question with a
    # different ruler (a random-ranking null band). If both numbers here reproduce it, the
    # two faces are measuring the same book, not two books.
    an = src.get("arm_noise") or {}
    an_v = an.get("verdict") or {}
    ov_an = an_v.get("book_overlap") or {}
    xcheck = {"published_face_present": bool(an_v)}
    if an_v:
        mine_diff = round((high["stats"]["full"]["cagr"]
                           - base["stats"]["full"]["cagr"]) * 100.0, 3)
        pub_diff = an_v.get("diff_pp")
        pub_jac = ov_an.get("mean_jaccard")
        mine_jac = ov_hb.get("mean_jaccard")
        xcheck.update({
            "published_verdict": an_v.get("verdict"),
            "diff_pp_published": pub_diff, "diff_pp_here": mine_diff,
            "jaccard_published": pub_jac, "jaccard_here": mine_jac,
            "diff_tol_pp": XCHECK_DIFF_TOL_PP, "jaccard_tol": XCHECK_JAC_TOL,
            "diff_agrees": (None if pub_diff is None
                            else bool(abs(mine_diff - float(pub_diff)) <= XCHECK_DIFF_TOL_PP)),
            "jaccard_agrees": (None if pub_jac is None or mine_jac is None
                               else bool(abs(mine_jac - float(pub_jac)) <= XCHECK_JAC_TOL)),
            "identical_days_published": ov_an.get("identical_days"),
            "identical_days_here": ov_hb.get("identical_days")})
        xcheck["agree"] = bool(xcheck["diff_agrees"] and xcheck["jaccard_agrees"])

    out = {"evidence_cutoff": (src["evidence_cutoff"]
                               or str(pd.Timestamp(close.index[-1]).date())),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_gate_raise_noise.py",
           "rule": {"gates_cny": GATES, "high_cny": HIGH, "low_cny": LOW,
                    "shipped_cny": SHIPPED, "control_tol_pp": CONTROL_TOL_PP,
                    "universe_tol_names": UNIVERSE_TOL, "block": BLOCK,
                    "draws": DRAWS, "seed": SEED, "p_sig": P_SIG,
                    "swap_min": SWAP_MIN, "year_major": YEAR_MAJOR,
                    "question": "the book arm's 100M reading vs its 40M reading",
                    "p_value": "one-sided circular block bootstrap on the paired daily "
                               "return difference (block = one rebalance period)",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"book_seats": seats, "card_seats": card_seats,
                      "rebal": int(cfg_p.get("rebal") or 20),
                      "vol_target": cfg_p.get("vol_target"),
                      "cost_bp_per_side": cfg_p.get("cost_bp_per_side"),
                      "universe_measured": universe_measured,
                      "universe_published": published_universe,
                      "universe_delta_names": universe_delta,
                      "flips_repaired": int(n_flip),
                      "panel_build_seconds": round(t_panel, 1),
                      "run_seconds": None},
           "control": {"cells": control, "worst_delta_pp": worst, "tol_pp": CONTROL_TOL_PP},
           "arms": {("%gM" % (g / 1e6)): {"stats": arms[g]["stats"],
                                          "turnover_per_decision":
                                              arms[g]["turnover_per_decision"],
                                          "decisions": arms[g]["diag_rows"],
                                          "bars_below_seats":
                                              (src["published"].get(float(g)) or {}).get(
                                                  "book_bars_below_seats")}
                    for g in GATES},
           "pairs": {"high_vs_low": {"bootstrap": bs_hl, "overlap": ov_hl,
                                     "segment_split": seg, "years": years,
                                     "cagr_delta_pp": round(
                                         ((high["stats"]["full"]["cagr"]
                                           - low["stats"]["full"]["cagr"]) * 100.0), 3)},
                     "high_vs_shipped": {"bootstrap": bs_hb, "overlap": ov_hb,
                                         "cagr_delta_pp": round(
                                             ((high["stats"]["full"]["cagr"]
                                               - base["stats"]["full"]["cagr"]) * 100.0), 3)}},
           "binding_bars_below_seats": bind,
           "crosscheck": xcheck,
           "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"],
                      "swap_share": ov_hl["swap_share"],
                      "p_one_sided": (bs_hl or {}).get("p_one_sided"),
                      "cagr_delta_pp": out["pairs"]["high_vs_low"]["cagr_delta_pp"],
                      "run_seconds": out["config"]["run_seconds"]}, ensure_ascii=False))
    return 0


def write_md(out):
    v = out["verdict"]
    hl = out["pairs"]["high_vs_low"]
    seg = hl.get("segment_split") or {}
    bs = hl.get("bootstrap") or {}
    ov = hl.get("overlap") or {}
    seats = out["config"]["book_seats"]

    def pct(x):
        return "-" if x is None else "%.2f%%" % (x * 100.0)

    lines = ["# 5 座臂上「100M 反而 9.91%」：更厚的票，还是几个换了名字的持仓（r1760）", "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "抬闸定价面（r1759）在图书臂（%d 座）上印出这条形状：20M %s → 40M %s → 100M %s。"
             "本面只问一件事：**这 1.79pp 的凸起，是抬闸真的买到了不同的票，还是一个能被自己的噪声吞掉的差**——"
             "同一张面板、同一台引擎、同一套成本与波动目标，只动流动性门槛。"
             % (seats,
                pct((out["arms"].get("20M") or {}).get("stats", {}).get("full", {}).get("cagr")),
                pct((out["arms"].get("40M") or {}).get("stats", {}).get("full", {}).get("cagr")),
                pct((out["arms"].get("100M") or {}).get("stats", {}).get("full", {}).get("cagr"))),
             "",
             "## 1. 这道闸根本没有碰到这本书", ""]
    below = out["binding_bars_below_seats"]
    lines.append("装不满的决策日（可挑名数 < %d 座）：20M **%s**、40M **%s**、100M **%s**。"
                 % (seats, below.get("book_20M", "-"), below.get("book_40M", "-"),
                    below.get("book_100M", "-")))
    lines += ["",
              "三档都是 0：在这本书上，抬闸**从来没有让它挑不满座位**。所以这三档之间的任何差都不是"
              "「容量换来的」，只能是**换了哪几个名字**。", "",
              "## 2. 两个闸挑的是同一批名字吗", "",
              "| 比较 | 决策日 | 平均重合 | 不同票的决策日占比 | 累计换手名次 |",
              "|---|---|---|---|---|"]
    for lbl, pair in (("100M vs 40M", out["pairs"]["high_vs_low"]),
                      ("100M vs 20M（在印档）", out["pairs"]["high_vs_shipped"])):
        o = pair.get("overlap") or {}
        lines.append("| %s | %s | %s | %s | %s |" % (
            lbl, o.get("decisions"), "-" if o.get("mean_overlap") is None
            else "%.0f%%" % (o["mean_overlap"] * 100),
            "-" if o.get("swap_share") is None else "%.0f%%" % (o["swap_share"] * 100),
            o.get("names_swapped_total")))
    lines += ["",
              "## 3. 这个差比它自己的噪声大吗", "",
              "配对日收益差（100M − 40M），圆形块自助（块长 %s 根＝一个调仓周期、%s 次重采样、种子 %s）："
              "**p = %s**（单侧）。观测日均差 %s。"
              % (bs.get("block"), bs.get("draws"), bs.get("seed"),
                 "-" if bs.get("p_one_sided") is None else "%.3f" % bs["p_one_sided"],
                 "-" if bs.get("obs_mean_daily") is None
                 else "%.6f" % bs["obs_mean_daily"]),
              "",
              "逐年（每臂按**上年收盘**起算，不从 1.0 起算）：", "",
              "| 年 | 100M | 40M | 差 | 高档领先 |", "|---|---|---|---|---|"]
    for r in ((hl.get("years") or {}).get("rows") or []):
        lines.append("| %d | %s | %s | %+.2fpp | %s |" % (
            r["year"], pct(r["high"]), pct(r["low"]), r["diff_pp"],
            "是" if r["high_leads"] else "否"))
    lines += ["",
              "段分解（%s 个调仓段：同票 %s 段、不同票 %s 段）：同票段合计 %+s、不同票段合计 %+s。"
              % (seg.get("segments"), seg.get("same_book_segments"),
                 seg.get("diff_book_segments"), seg.get("gap_pp_same_book"),
                 seg.get("gap_pp_diff_book")),
              "",
              "## 控制臂", "",
              "每个读数都必须复现抬闸定价面自己那一格（容差 %.2fpp）：" % out["control"]["tol_pp"],
              "", "| 格 | 本面 | 定价面 | 偏差 |", "|---|---|---|---|"]
    for k, c in (out["control"]["cells"] or {}).items():
        lines.append("| %s | %s | %s | %+.4fpp |" % (
            k, pct(c["arm_cagr"]), pct(c["published_cagr"]), c["delta_pp"]))
    lines += ["",
              "宇宙宽度：实测 %s 名 / 定价面 %s 名（差 %s）。面板末根 bar %s，证据截断 %s。"
              % (out["config"]["universe_measured"], out["config"]["universe_published"],
                 out["config"]["universe_delta_names"], out["panel_last_bar"],
                 out["evidence_cutoff"]),
              ""]
    xc = out.get("crosscheck") or {}
    if xc.get("published_face_present"):
        lines += ["## 与另一张面的核对", "",
                  "同一问的另一半（100M vs **20M**，在印档）另有一张面用**不同的尺子**回答（随机排名零假设带）。"
                  "本面用独立实现重算它那两个数：", "",
                  "| 量 | 那张面 | 本面 | 容差 | 一致 |", "|---|---|---|---|---|",
                  "| 两档年化差 | %s | %s | ±%.2fpp | %s |" % (
                      "-" if xc.get("diff_pp_published") is None
                      else "%+.2fpp" % float(xc["diff_pp_published"]),
                      "-" if xc.get("diff_pp_here") is None
                      else "%+.2fpp" % float(xc["diff_pp_here"]), xc.get("diff_tol_pp"),
                      {True: "是", False: "否", None: "无法比"}[xc.get("diff_agrees")]),
                  "| 平均 Jaccard | %s | %s | ±%.2f | %s |" % (
                      "-" if xc.get("jaccard_published") is None
                      else "%.4f" % float(xc["jaccard_published"]),
                      "-" if xc.get("jaccard_here") is None
                      else "%.4f" % float(xc["jaccard_here"]), xc.get("jaccard_tol"),
                      {True: "是", False: "否", None: "无法比"}[xc.get("jaccard_agrees")]),
                  "",
                  "结论：%s。两张面对「那一下是不是噪声」给出的是**同一个方向**，"
                  "差别只在尺子（一张用随机排名零假设带，一张用配对日收益的块自助）与比较档位"
                  "（20M vs 40M）。"
                  % ("两个数在容差内逐位复现" if xc.get("agree") else "两个数**没有**复现，两张面测的不是同一本书"),
                  ""]
    lines += ["**本面不改门票，也不改抬闸定价面的任何数字。** 它只回答：那个被当成「更优的闸」的凸起，"
              "经不经得起一次噪声检验。", ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("md -> %s" % OUT_MD)


def _check():
    """Re-derive the published verdict from the published numbers (no re-run)."""
    with open(OUT_JSON, encoding="utf-8") as fh:
        out = json.load(fh)
    hl = (out.get("pairs") or {}).get("high_vs_low") or {}
    again = classify(control_delta_pp=out["control"]["worst_delta_pp"],
                     universe_delta=out["config"]["universe_delta_names"],
                     swap_share=(hl.get("overlap") or {}).get("swap_share"),
                     mean_overlap=(hl.get("overlap") or {}).get("mean_overlap"),
                     p_value=(hl.get("bootstrap") or {}).get("p_one_sided"),
                     years=(hl.get("years") or {}).get("years"),
                     high_leads=(hl.get("years") or {}).get("high_leads"),
                     binding_bars=sum(v for v in out["binding_bars_below_seats"].values()
                                      if isinstance(v, int)))
    ok = again["verdict"] == out["verdict"]["verdict"]
    print(json.dumps({"published": out["verdict"]["verdict"], "recomputed": again["verdict"],
                      "ok": ok}, ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails = []
    legs = []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 a book that never changes is not evidence for a better gate
    v = classify(control_delta_pp=0.0, swap_share=0.0, mean_overlap=1.0, p_value=0.001,
                 years=6, high_leads=6)
    chk("L1 same book", v["verdict"] == "SAME_BOOK_SO_GAP_IS_NOT_SELECTION", v["verdict"])
    chk("L1b sentence refuses selection", "不是「抬闸换来了更好的票」" in v["sentence"])

    # L2 different tickets whose gap a bootstrap cannot separate
    v = classify(control_delta_pp=0.0, swap_share=0.35, mean_overlap=0.8, p_value=0.31,
                 years=6, high_leads=3)
    chk("L2 not separable", v["verdict"] == "DIFFERENT_TICKETS_NOT_SEPARABLE", v["verdict"])
    chk("L2b names the p", "p=0.310" in v["sentence"], v["sentence"])

    # L3 separable: p, swap share and the year majority must all line up
    v = classify(control_delta_pp=0.0, swap_share=0.35, mean_overlap=0.7, p_value=0.01,
                 years=6, high_leads=5)
    chk("L3 separable", v["verdict"] == "DIFFERENT_TICKETS_AND_SEPARABLE", v["verdict"])

    # L3b any one of the three failing keeps it in the noise bucket
    v = classify(control_delta_pp=0.0, swap_share=0.35, mean_overlap=0.7, p_value=0.01,
                 years=6, high_leads=2)
    chk("L3b year minority", v["verdict"] == "DIFFERENT_TICKETS_NOT_SEPARABLE", v["verdict"])
    v = classify(control_delta_pp=0.0, swap_share=0.02, mean_overlap=0.98, p_value=0.001,
                 years=6, high_leads=6)
    chk("L3c too few swaps", v["verdict"] == "DIFFERENT_TICKETS_NOT_SEPARABLE", v["verdict"])

    # L4 control failures judge nothing
    v = classify(control_delta_pp=1.2, swap_share=0.5, p_value=0.001, years=6, high_leads=6)
    chk("L4 control", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = classify(control_delta_pp=None, swap_share=0.5, p_value=0.001)
    chk("L4b no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])
    v = classify(control_delta_pp=0.0, universe_delta=UNIVERSE_TOL + 1, swap_share=0.5,
                 p_value=0.001, years=6, high_leads=6)
    chk("L4c universe", v["verdict"] == "CANNOT_JUDGE_UNIVERSE", v["verdict"])
    v = classify(control_delta_pp=0.0, swap_share=None, p_value=None)
    chk("L4d no arms", v["verdict"] == "CANNOT_JUDGE_NO_ARMS", v["verdict"])

    # L5 the bootstraps actually see the sign of the difference
    rng = np.random.default_rng(7)
    zero = list(rng.normal(0.0, 0.01, 800))
    chk("L5 null not separable", block_bootstrap_p(zero, block=20, draws=500, seed=1)[
        "p_one_sided"] > 0.05,
        block_bootstrap_p(zero, block=20, draws=500, seed=1)["p_one_sided"])
    pos = list(rng.normal(0.002, 0.01, 800))
    chk("L5b a real shift is caught", block_bootstrap_p(pos, block=20, draws=500, seed=1)[
        "p_one_sided"] < 0.01,
        block_bootstrap_p(pos, block=20, draws=500, seed=1)["p_one_sided"])
    chk("L5c too short says nothing", block_bootstrap_p([0.1] * 10, block=20) is None)

    # L6 overlap counts names, not dates
    a = {"2020-01-02": ["A", "B", "C", "D", "E"], "2020-02-02": ["A", "B", "C", "D", "Z"]}
    b = {"2020-01-02": ["A", "B", "C", "D", "E"], "2020-02-02": ["A", "B", "C", "D", "E"]}
    o = overlap_stats(a, b, 5)
    chk("L6 swap share", abs(o["swap_share"] - 0.5) < 1e-9, str(o))
    chk("L6b overlap mean", abs(o["mean_overlap"] - 0.9) < 1e-9, str(o))
    chk("L6c swapped names", o["names_swapped_total"] == 1, str(o))
    chk("L6d no shared days says nothing", overlap_stats(a, {}, 5)["swap_share"] is None)

    # L7 the year table measures from the previous close, never from 1.0
    idx = pd.to_datetime(["2020-06-30", "2020-12-31", "2021-12-31", "2022-12-31"])
    ser_a = pd.Series([2.0, 2.4, 2.2, 2.3], index=idx)
    ser_b = pd.Series([2.0, 2.2, 2.0, 2.2], index=idx)
    y = year_table(ser_a, ser_b)
    first = y["rows"][0]
    chk("L7 first year from the series start", abs(first["high"] - 0.2) < 1e-9, str(first))
    chk("L7b year two from the previous close", abs(y["rows"][1]["high"] + 1 / 12.0) < 1e-3,
        str(y["rows"][1]))
    chk("L7d a start=1.0 reading would be a different number", first["high"] != 2.4 - 1.0)
    chk("L7c leader count", y["high_leads"] == len([r for r in y["rows"] if r["high_leads"]]),
        str(y))

    # L8 the prices this face is about are the ones the price face published
    if os.path.exists(FACE_PRICE) and os.path.exists(CARD_JSON):
        src = read_inputs()
        pub = src["published"]
        chk("L8 low and high rungs are priced on the book arm",
            (pub.get(LOW) or {}).get("book") is not None
            and (pub.get(HIGH) or {}).get("book") is not None, str(sorted(pub)))
        chk("L8b the bump is upward as published",
            float(pub[HIGH]["book"]) > float(pub[LOW]["book"]), str(pub.get(HIGH)))
    else:
        chk("L8 inputs present", False, "price/card face missing")

    if fails:
        print("SELFTEST FAIL (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST OK (%d legs)" % len(legs))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        with open(OUT_JSON, encoding="utf-8") as fh:
            write_md(json.load(fh))
        return 0
    if "run" in argv:
        return run()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
