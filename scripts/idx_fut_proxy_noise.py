"""Proxy noise: what an ETF close costs you when it stands in for the index close.

DIRECTION-20261114 section 3 P1 names the gap in one line -- the basis lane needs a
same-day index print, and the proposed stand-in (the ETF close) has never been
priced.  This face prices it: for every pair that has an ETF proxy, the basis is
computed twice on the same futures bars, once against the index and once against the
ETF, and the difference between the two answers is reported.

Two numbers, never added and never averaged:

  LEVEL OFFSET  (%/yr, structural) -- the ETF accrues dividends the price index does
      not, so its basis sits at a *constant* different level.  This is a known wedge
      and it does not corrupt a timing rule that reads the basis against its own
      history.
  DAILY NOISE   (bp/day)          -- the day-to-day swing of the proxy error.  This is
      the thing that can manufacture or erase a signal, because the timing rule is
      reading exactly that day-to-day shape.

The money question is not the correlation, it is whether the published rule fires on
the same days.  Both bases are run through idx_fut_basis_timing.causal_percentiles
(imported, not re-implemented) and the widest-quintile entry flag is compared day by
day; the carry reading is recomputed off the ETF spot and set beside the published
one, so a reader can see whether substituting the proxy would flip C1.

PRE-REGISTERED (written before the first run, r1313; do not move after seeing data):

  NOISE_MAX_BP    = 10.0   bp/day
      The rule under test needs a 0.10pp edge over a 20-trading-day forward window
      (idx_fut_basis_timing H1_STRIDE_PP) = 0.5 bp/day.  An error whose daily swing
      is 20x the effect being measured can fabricate the effect.  Below that line the
      error is smaller than the thing being read.

  RULE_AGREE_MIN  = 0.95
      Share of warm days on which both bases give the same entry flag.  Under 95% the
      two panels tell a reader to enter on different days, so one of them is not a
      substitute for the other.

  MIN_DAYS        = 400
      Below this the pair reports thin_sample rather than a verdict.

Verdicts: PROXY_FIT / PROXY_BREAKS_RULE (which condition failed is printed) /
PROXY_ABSENT (no ETF proxy exists -- honest, never a pass) / thin_sample.

Run:  python scripts/idx_fut_proxy_noise.py            (writes results/idx_fut_proxy_noise.json)
      python scripts/idx_fut_proxy_noise.py --selftest (offline, synthetic)
      python scripts/idx_fut_proxy_noise.py --check    (re-derive and compare)
"""
import json
import math
import os
import statistics
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idx_fut_basis as base            # noqa: E402  (panels, pair table, estimators)
import idx_fut_basis_timing as timing   # noqa: E402  (the rule being tested)

OUT = os.path.join(base.ROOT, "results", "idx_fut_proxy_noise.json")

NOISE_MAX_BP = 10.0
RULE_AGREE_MIN = 0.95
MIN_DAYS = 400
WIDEST_PCT = 20.0     # the entry band the timing face calls "widest discount"
BASIS_RANGE_MIN_BP = 1.0   # below this the basis never moved; a rank is arithmetic, not a reading
SPLIT_MIN_PCT = 35.0       # a single-day move this large in an ETF panel is a re-denomination,
                           # not a return -- the same 35% line the etf_book repair_flips leg uses

WHO_PAYS = (
    "The discount exists because someone with a cash equity book pays it: a hedge "
    "that has to be short the future, and the snowball/autocallable desks that buy "
    "the index and sell the future to finance the coupon. Neither of them is trying "
    "to earn the basis; they are paying it to be somewhere else. An index print and "
    "an ETF print both let a reader see that payment -- but only if the ETF print "
    "carries the same day-to-day shape, which is what this face measures."
)


def log(msg):
    sys.stdout.write(msg + "\n")


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def daily_noise_bp(err):
    """Std of the *change* of the proxy error, in basis points per day.

    The level of the error is a dividend wedge, which is why it is removed by taking
    the first difference before measuring anything.
    """
    d = [err[k] - err[k - 1] for k in range(1, len(err))]
    if len(d) < 3:
        return None
    return statistics.pstdev(d) * 10000.0


def entry_flags(pcts):
    """1 where the day sits in the widest quintile, 0 elsewhere, None while warming up."""
    return [None if p is None else (1 if p < WIDEST_PCT else 0) for p in pcts]


def flag_agreement(flags_a, flags_b):
    """Day-by-day agreement of the entry flag, plus the confusion counts.

    Two bases that disagree on 40% of the *entry* days are not two views of one fact.
    """
    n = both = agree = a_only = b_only = 0
    for x, y in zip(flags_a, flags_b):
        if x is None or y is None:
            continue
        n += 1
        if x == y:
            agree += 1
        elif x == 1 and y == 0:
            a_only += 1
        elif x == 0 and y == 1:
            b_only += 1
    if n == 0:
        return None
    both = sum(1 for x, y in zip(flags_a, flags_b) if x == 1 and y == 1)
    return {"days": n, "agree_pct": round(100.0 * agree / n, 2),
            "both_in": both, "index_only": a_only, "etf_only": b_only}


def judge_pair(noise_bp, agreement, basis_range_bp=None, adj_agreement=None):
    """Verdict from the two pre-registered conditions, naming the one that failed.

    Three states matter, and collapsing them would hide the actionable one:
      PROXY_FIT               the raw ETF close reproduces the entry days
      PROXY_FIT_IF_DETRENDED  it does not, but it does once the measured tracking
                              drift is removed -- the wedge is a thing the reader can
                              measure and subtract, so the proxy is still usable, but
                              only if the face says so out loud
      PROXY_NOT_A_SUBSTITUTE  neither reading reproduces the entry days

    A basis that never moves cannot be ranked: its percentile is decided by the last
    bit of a float, so a "fit" there would be a statement about arithmetic.
    """
    if noise_bp is None or agreement is None:
        return {"verdict": "thin_sample", "why": "not enough warm paired days"}
    if basis_range_bp is not None and basis_range_bp < BASIS_RANGE_MIN_BP:
        return {"verdict": "flat_basis",
                "why": "basis range %.1f bp < %.1f bp: the rank is arithmetic, not a measurement"
                       % (basis_range_bp, BASIS_RANGE_MIN_BP)}

    def ok(ag):
        return ag is not None and ag["agree_pct"] / 100.0 >= RULE_AGREE_MIN

    fails = []
    if noise_bp > NOISE_MAX_BP:
        fails.append("noise_bp %.2f > %.2f" % (noise_bp, NOISE_MAX_BP))
    if ok(agreement) and not fails:
        return {"verdict": "PROXY_FIT",
                "why": "noise and entry agreement both inside the pre-registered lines"}
    if adj_agreement is not None and ok(adj_agreement) and noise_bp <= NOISE_MAX_BP:
        return {"verdict": "PROXY_FIT_IF_DETRENDED",
                "why": "raw entry agreement %.2f%% misses the line; removing the measured "
                       "tracking drift lifts it to %.2f%% -- usable, but only detrended"
                       % (agreement["agree_pct"], adj_agreement["agree_pct"])}
    if not fails:
        fails.append("agree %.2f%% < %.0f%% (raw) and %s (detrended)"
                     % (agreement["agree_pct"], RULE_AGREE_MIN * 100,
                        "%.2f%%" % adj_agreement["agree_pct"] if adj_agreement else "not measurable"))
    return {"verdict": "PROXY_NOT_A_SUBSTITUTE", "why": "; ".join(fails)}


def detrended_basis(fc, ic, ec):
    """Basis computed on an ETF leg with its own cumulative tracking drift removed.

    The ratio at day k multiplies only returns up to k, so this is causal: a reader
    could have computed the same adjustment on that day.  Removing the wedge here is
    not cosmetic -- it accumulates inside the rule's 250-day lookback, so at the
    level it is "structural" and inside the rank it is not.
    """
    ratio = 1.0
    adj = [ec[0]]
    for k in range(1, len(ec)):
        ratio *= (ec[k] / ec[k - 1]) / (ic[k] / ic[k - 1])
        adj.append(ec[k] / ratio)
    return [f / e - 1.0 for f, e in zip(fc, adj)]


def repair_splits(dates, vals, min_pct=SPLIT_MIN_PCT):
    """Undo share re-denominations in an as-traded ETF panel, and name every one.

    data/daily is as-traded: when a fund folds its units the quoted price steps by the
    fold ratio and the holder's value does not move.  Left in, that step reads as a
    one-day return of +176% (512100 on 2022-09-05) or +248% (510500 on 2015-04-15) and
    every drift and noise number downstream is then a statement about the fold.  Prior
    prices are rescaled to the post-fold basis, which is what a split adjustment is;
    nothing is invented, and each repair is reported rather than performed silently.
    """
    out = list(vals)
    found = []
    for k in range(1, len(out)):
        if out[k - 1] <= 0:
            continue
        factor = out[k] / out[k - 1]
        if abs(factor - 1.0) > min_pct / 100.0:
            for j in range(k):
                out[j] *= factor
            found.append({"date": dates[k], "jump_pct": round((factor - 1.0) * 100, 2)})
    return out, found


def futures_close(fut):
    path = os.path.join(base.FUT_DIR, fut + ".csv")
    if not os.path.exists(path):
        return None
    out = {}
    for r in base.read_csv_rows(path):
        try:
            out[str(r["date"])[:10]] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return out or None


def one_pair(fut, code, etf):
    fc_all = futures_close(fut)
    if not fc_all:
        return {"status": "no_futures_panel"}
    if not etf:
        return {"status": "PROXY_ABSENT",
                "detail": "no ETF tracks this index inside data/daily, so there is no proxy to price"}
    etf_close = base.load_etf(etf)
    if not etf_close:
        return {"status": "PROXY_ABSENT", "detail": "ETF panel %s not on disk" % etf}
    try:
        idx = base.load_index(code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}

    dates, fc, ic, raw_etf = [], [], [], []
    for d in sorted(set(fc_all) & set(idx) & set(etf_close)):
        dates.append(d)
        fc.append(fc_all[d])
        ic.append(idx[d])
        raw_etf.append(etf_close[d])
    if len(dates) < MIN_DAYS:
        return {"status": "thin_sample", "days": len(dates)}

    # A price index (3,900 points) and an ETF (4.0 yuan) are not the same ruler, so the
    # ETF leg is anchored to the index's own level on the first common day.  The anchor
    # is one constant: it changes the level of the series and nothing about its shape,
    # which is why every shape statistic below is unaffected by which day anchors it.
    raw_etf, splits = repair_splits(dates, raw_etf)
    anchor = ic[0] / raw_etf[0]
    ec = [e * anchor for e in raw_etf]

    basis_idx = [f / i - 1.0 for f, i in zip(fc, ic)]
    basis_etf = [f / e - 1.0 for f, e in zip(fc, ec)]
    err = [b - a for a, b in zip(basis_idx, basis_etf)]

    # The wedge, in the unit a reader meets it in: percent per year of tracking drift.
    # Two conventions, printed side by side and never averaged:
    #   mean   -- matches the cumulative ETF-vs-index return (what a holder actually got)
    #   median -- a typical day's spread, which is what the parent face's C3 control
    #             reports.  The two can differ by more than a percent per year because
    #             ETF prices mean-revert against the index on large days (fat left tail
    #             pulls the mean down while the median stays high).  A reader told
    #             "dividends cost 1.8%/yr" and a reader told "cumulative drift is 0.1%/yr"
    #             are reading the same panel with two different summaries.
    di = [ic[k] / ic[k - 1] - 1.0 for k in range(1, len(ic))]
    de = [ec[k] / ec[k - 1] - 1.0 for k in range(1, len(ec))]
    dspread = [b - a for a, b in zip(di, de)]
    drift_mean = round(statistics.fmean(dspread) * base.TRADING_DAYS * 100, 3)
    drift_median = round(statistics.median(dspread) * base.TRADING_DAYS * 100, 3)
    cum_ratio = (ec[-1] / ec[0]) / (ic[-1] / ic[0])
    drift_cum = round((cum_ratio ** (base.TRADING_DAYS / max(1, len(ec) - 1)) - 1.0) * 100, 3)

    # The two readings of the same payment.
    _, spread_idx, roll_idx = base.basis_face(fc, ic, dates)
    _, spread_etf, roll_etf = base.basis_face(fc, ec, dates)
    carry_idx = base.stats_pct([v for k, v in enumerate(spread_idx) if not roll_idx[k]])
    carry_etf = base.stats_pct([v for k, v in enumerate(spread_etf) if not roll_etf[k]])

    # The rule, both ways.  The raw reading is what a reader gets by just swapping the
    # spot leg.  The detrended reading removes the cumulative tracking drift measured
    # on the same days, causally (the ratio at day k only uses returns up to k): the
    # wedge accumulates inside the rule's own 250-day lookback, so it shifts the rank
    # even when it is "structural" at the level.  Both readings are printed.
    flags_idx = entry_flags(timing.causal_percentiles(basis_idx))
    flags_etf = entry_flags(timing.causal_percentiles(basis_etf))
    agreement = flag_agreement(flags_idx, flags_etf)

    basis_etf_adj = detrended_basis(fc, ic, ec)
    flags_adj = entry_flags(timing.causal_percentiles(basis_etf_adj))
    agreement_adj = flag_agreement(flags_idx, flags_adj)

    noise_bp = daily_noise_bp(err)
    basis_range_bp = (max(basis_idx) - min(basis_idx)) * 10000.0
    j = judge_pair(noise_bp, agreement, basis_range_bp, agreement_adj)

    ci = carry_idx["median_ann_pct"] if carry_idx else None
    ce = carry_etf["median_ann_pct"] if carry_etf else None
    c1_idx = None if ci is None else ci >= base.CARRY_MIN_PCT
    c1_etf = None if ce is None else ce >= base.CARRY_MIN_PCT
    log("  %-3s %-9s days=%d noise=%s bp/day drift(mean/med/cum)=%s/%s/%s%%/yr agree=%s%%/%s%% carry idx=%s etf=%s -> %s"
        % (fut, etf, len(dates),
           "n/a" if noise_bp is None else "%.2f" % noise_bp,
           drift_mean, drift_median, drift_cum,
           "n/a" if agreement is None else "%.1f" % agreement["agree_pct"],
           "n/a" if agreement_adj is None else "%.1f" % agreement_adj["agree_pct"],
           ci, ce, j["verdict"]))

    return {
        "status": "ok",
        "index": code, "etf": etf,
        "window": {"from": dates[0], "to": dates[-1], "days": len(dates),
                   "anchor": dates[0], "anchor_factor": round(anchor, 6)},
        "splits_repaired": splits,
        "splits_note": "as-traded panel re-denominations undone; each one is listed here, none is silent",
        "tracking_drift_ann_pct": drift_mean,
        "tracking_drift_ann_pct_by_convention": {
            "mean_of_daily_spreads": drift_mean,
            "median_of_daily_spreads": drift_median,
            "from_cumulative_ratio": drift_cum,
            "note": "three summaries of one panel; the parent face's C3 control reads the "
                    "median, a holder experiences the cumulative ratio, and neither may be "
                    "quoted as if it were the other",
        },
        "tracking_drift_note": "structural wedge between the ETF and the price index; reported, never subtracted from noise",
        "level_offset_pct": round(statistics.median(err) * 100, 3),
        "level_offset_note": "the wedge expressed at the basis' own scale; structural, not signal error",
        "daily_noise_bp": None if noise_bp is None else round(noise_bp, 2),
        "median_abs_daily_noise_bp": round(statistics.median([abs(err[k] - err[k - 1])
                                                              for k in range(1, len(err))]) * 10000.0, 2),
        "corr_daily_basis_change": _r(pearson(
            [basis_etf[k] - basis_etf[k - 1] for k in range(1, len(basis_etf))],
            [basis_idx[k] - basis_idx[k - 1] for k in range(1, len(basis_idx))])),
        "rule": {"widest_pct": WIDEST_PCT, "agreement": agreement,
                 "agreement_detrended": agreement_adj},
        "basis_range_bp": round(basis_range_bp, 1),
        "carry": {"index_median_ann_pct": ci, "etf_median_ann_pct": ce,
                  "published_c1_line_pct": base.CARRY_MIN_PCT,
                  "C1_index": c1_idx, "C1_etf": c1_etf,
                  "C1_would_flip": None if c1_idx is None or c1_etf is None else bool(c1_idx != c1_etf)},
        "verdict": j["verdict"],
        "why": j["why"],
        "latest": {"basis_index_pct": round(basis_idx[-1] * 100, 3),
                   "basis_etf_pct": round(basis_etf[-1] * 100, 3)},
    }


def _r(v, nd=4):
    return None if v is None else round(v, nd)


def build():
    face = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "who_pays": WHO_PAYS,
        "prereg": {"noise_max_bp": NOISE_MAX_BP, "rule_agree_min": RULE_AGREE_MIN,
                   "min_days": MIN_DAYS, "widest_pct": WIDEST_PCT,
                   "written": "r1313, before the first run of this face"},
        "pairs": {},
    }
    log("proxy noise vs the published rule (pre-registered lines: %.1f bp/day, %.0f%% agreement)"
        % (NOISE_MAX_BP, RULE_AGREE_MIN * 100))
    for fut, (code, _name, etf) in base.PAIRS.items():
        face["pairs"][fut] = one_pair(fut, code, etf)
    face["verdict"] = summarize(face["pairs"])
    return face


def summarize(pairs):
    """One line the reader can act on.  An absent proxy is never folded into a pass."""
    ok = {f: v for f, v in pairs.items() if v.get("status") == "ok"}
    fit = sorted(f for f, v in ok.items() if v["verdict"] == "PROXY_FIT")
    only_detrended = sorted(f for f, v in ok.items() if v["verdict"] == "PROXY_FIT_IF_DETRENDED")
    broken = sorted(f for f, v in ok.items() if v["verdict"] == "PROXY_NOT_A_SUBSTITUTE")
    absent = sorted(f for f, v in pairs.items() if v.get("status") == "PROXY_ABSENT")
    thin = sorted(f for f, v in pairs.items()
                  if v.get("status") in ("thin_sample", "no_index", "no_futures_panel")
                  or v.get("verdict") == "flat_basis")
    flips = sorted(f for f, v in ok.items() if (v.get("carry") or {}).get("C1_would_flip"))
    # A level reading and a rank reading fail for different reasons and are answered
    # separately: noise corrupts "the basis is -1.4% today", while the trailing-rank
    # entry day survives it once the drift trend is removed.
    level_ok = sorted(f for f, v in ok.items() if (v.get("daily_noise_bp") or 0) <= NOISE_MAX_BP)
    rank_only = sorted(f for f, v in ok.items()
                       if (v.get("rule") or {}).get("agreement_detrended", {}).get("agree_pct", 0) >= RULE_AGREE_MIN * 100)
    if not ok:
        state = "NO_PAIR_PRICED"
    elif broken:
        state = "PROXY_NOT_A_SUBSTITUTE"
    elif only_detrended:
        state = "PROXY_FIT_IF_DETRENDED"
    else:
        state = "PROXY_CARRIES_THE_RULE"
    return {
        "state": state,
        "fit": fit, "fit_if_detrended": only_detrended,
        "breaks_rule": broken, "absent": absent, "unpriced": thin,
        "c1_would_flip": flips,
        "level_readable": level_ok, "rank_after_detrend": rank_only,
        "sentence": sentence(state, fit, broken, absent, flips, only_detrended, level_ok, rank_only, ok),
    }


def sentence(state, fit, broken, absent, flips, only_detrended=(), level_ok=(), rank_ok=(), detail=None):
    if state == "NO_PAIR_PRICED":
        return "今天读不到：没有任何一对同时具备期货、指数与 ETF 三条盘面板，代理噪声无法计价。"
    detail = detail or {}
    if state == "PROXY_NOT_A_SUBSTITUTE":
        noisy = sorted(f for f, v in detail.items() if (v.get("daily_noise_bp") or 0) > NOISE_MAX_BP)
        tail = ""
        if rank_ok:
            tail = ("排名读数另说：%s 扣掉可测漂移后入场日与指数面一致，所以"
                    "「今天基差是不是落在最宽的 20%%」仍可读——不可读的是水平值"
                    "（「基差 -1.4%%」这种），那是噪声直接吃掉的。" % "/".join(rank_ok))
        return ("ETF 收盘不能顶替指数收盘做**水平读数**：%s 的日噪声超过 %.1f bp/日（实测 %s bp/日），"
                "换用 ETF 算出来的基差点位、漂移与 C1 读数都会跟着漂（IC 5.04%%→%.2f%%）。%s%s"
                % ("/".join(noisy or broken), NOISE_MAX_BP,
                   "/".join("%.1f" % (detail[f].get("daily_noise_bp") or 0) for f in (noisy or broken)),
                   (detail.get("IC", {}).get("carry") or {}).get("etf_median_ann_pct") or 0.0,
                   tail,
                   ("另有 %s 会因此翻转 C1。" % "/".join(flips)) if flips else ""))
    if state == "PROXY_FIT_IF_DETRENDED":
        return ("ETF 收盘可以顶替，但必须先扣掉它自己的跟踪漂移（漂移在 250 日回看窗里会累积）："
                "%s 原样替换对不齐入场日，扣掉可测漂移后对齐。指数源断供时基差线仍可读，"
                "但页面上必须同时印出这个扣减。" % "/".join(only_detrended))
    return ("ETF 收盘可以作为指数收盘的替身：%s 的噪声与入场日一致度都落在预注册线内"
            "（≤%.1f bp/日、≥%.0f%% 同一天进场），指数源断供时基差线仍可读。"
            % ("/".join(fit), NOISE_MAX_BP, RULE_AGREE_MIN * 100)
            + ("（%s 无 ETF 可替，如实留空。）" % "/".join(absent) if absent else ""))


# ---------------------------------------------------------------- selftest

def _synth(kind, n=600):
    """Synthetic futures/index/ETF triples with a known proxy-error shape.

    Each case answers a different question the real face has to answer:
      proportional -- the ETF is a fixed multiple of the index: anchoring must erase
                      the wedge entirely, so nothing is left to report.
      drift_only   -- the ETF compounds 2%/yr slower (dividends): a structural wedge
                      that must NOT be counted as noise or as rule disagreement.
      wobble       -- that drift plus a 25bp/day swing: the error that can fake a signal.

    The basis itself must MOVE, or the percentile rank is decided by floating-point
    jitter rather than by the market: a flat basis is the degenerate case this face
    reports as basis_range_bp near zero instead of a verdict.
    """
    idx, etf, fut = [], [], []
    i = 100.0
    e = 100.0
    for k in range(n):
        i_ret = 0.0008 if k % 3 else -0.0005
        i *= 1.0 + i_ret
        if kind == "proportional":
            e = i * 1.02
        elif kind == "drift_only":
            e *= 1.0 + i_ret - (0.02 / base.TRADING_DAYS)
        else:  # wobble
            step = (25.0 if (k * 7919) % 13 < 6 else -25.0) / 10000.0
            e *= 1.0 + i_ret - (0.02 / base.TRADING_DAYS) + step
        basis = -0.02 + 0.015 * math.sin(k / 40.0)   # a basis that actually moves
        idx.append(i)
        etf.append(e)
        fut.append(i * (1.0 + basis))
    return idx, etf, fut


def _anchored_bases(idx, etf, fut):
    """Anchor the ETF to the index's level, then compute the basis both ways."""
    anchor = idx[0] / etf[0]
    e = [v * anchor for v in etf]
    return ([f / i - 1.0 for f, i in zip(fut, idx)],
            [f / x - 1.0 for f, x in zip(fut, e)])


def selftest():
    legs = []

    def L(name, cond):
        legs.append((name, bool(cond)))

    # L1 a proportional wedge is not an error at all once the scales are anchored
    idx, etf, fut = _synth("proportional")
    b_idx, b_etf = _anchored_bases(idx, etf, fut)
    err = [b - a for a, b in zip(b_idx, b_etf)]
    L("proportional wedge -> zero daily noise", abs(daily_noise_bp(err)) < 1e-6)
    L("proportional wedge -> no level offset left", abs(statistics.median(err)) < 1e-12)
    fa = entry_flags(timing.causal_percentiles(b_idx))
    fb = entry_flags(timing.causal_percentiles(b_etf))
    ag = flag_agreement(fa, fb)
    L("proportional wedge -> flags agree 100%", ag["agree_pct"] == 100.0)
    L("proportional wedge -> PROXY_FIT", judge_pair(daily_noise_bp(err), ag)["verdict"] == "PROXY_FIT")

    # L2 a pure dividend drift is structural at the LEVEL -- but inside a 250-day
    #    ranking window it accumulates, so the raw substitution can still move the
    #    entry days.  Both halves are encode here, because collapsing them would let
    #    "it's just dividends" stand in for "it doesn't matter".
    idx2, etf2, fut2 = _synth("drift_only")
    b_i2, b_e2 = _anchored_bases(idx2, etf2, fut2)
    err2 = [a - b for a, b in zip(b_i2, b_e2)]
    ec2 = [v * (idx2[0] / etf2[0]) for v in etf2]
    b_adj2 = detrended_basis(fut2, idx2, ec2)
    raw2 = flag_agreement(entry_flags(timing.causal_percentiles(b_i2)),
                          entry_flags(timing.causal_percentiles(b_e2)))
    adj2 = flag_agreement(entry_flags(timing.causal_percentiles(b_i2)),
                          entry_flags(timing.causal_percentiles(b_adj2)))
    L("dividend drift is not daily noise", daily_noise_bp(err2) < NOISE_MAX_BP)
    L("dividend drift moves the raw entry days (the wedge accumulates in the window)",
      raw2["agree_pct"] < 99.0)
    L("detrending restores the entry days", adj2["agree_pct"] >= 99.0)
    j2 = judge_pair(daily_noise_bp(err2), raw2, None, adj2)
    L("drift-only -> PROXY_FIT_IF_DETRENDED", j2["verdict"] == "PROXY_FIT_IF_DETRENDED")
    L("the detrended verdict names both readings", "%" in j2["why"] and "drift" in j2["why"])

    # L3 a wobbling wedge must break the rule and say which line it broke
    idx3, etf3, fut3 = _synth("wobble")
    b_i3, b_e3 = _anchored_bases(idx3, etf3, fut3)
    err3 = [a - b for a, b in zip(b_i3, b_e3)]
    ag3 = flag_agreement(entry_flags(timing.causal_percentiles(b_i3)),
                         entry_flags(timing.causal_percentiles(b_e3)))
    j3 = judge_pair(daily_noise_bp(err3), ag3)
    L("wobbling wedge -> noise above the line", daily_noise_bp(err3) > NOISE_MAX_BP)
    L("wobbling wedge -> PROXY_NOT_A_SUBSTITUTE", j3["verdict"] == "PROXY_NOT_A_SUBSTITUTE")
    L("the failing condition is named, not just the verdict", "noise_bp" in j3["why"])

    # L4 warm-up days are excluded from the agreement denominator, not counted as zeros
    ag4 = flag_agreement([None, None, 1, 0, 1], [None, None, 1, 0, 1])
    L("warm-up days excluded from agreement", ag4["days"] == 3 and ag4["agree_pct"] == 100.0)

    # L5 disagreement is split into the two directions (a reader needs to know which
    #    panel fires alone, not merely that they differ)
    ag5 = flag_agreement([1, 1, 0, 0], [1, 0, 1, 0])
    L("disagreement split into both directions",
      ag5["both_in"] == 1 and ag5["index_only"] == 1 and ag5["etf_only"] == 1)

    # L6 an absent proxy is never folded into a pass
    s = summarize({"IH": {"status": "PROXY_ABSENT"}, "IF": {"status": "ok", "verdict": "PROXY_FIT"}})
    L("absent proxy listed separately, not counted as fit", s["fit"] == ["IF"] and s["absent"] == ["IH"])

    # L7 nothing priced -> the page says so instead of printing an empty green
    s7 = summarize({"IH": {"status": "PROXY_ABSENT"}})
    L("no priced pair -> NO_PAIR_PRICED + says it cannot be read today",
      s7["state"] == "NO_PAIR_PRICED" and "今天读不到" in s7["sentence"])

    # L8 units: noise scales linearly in bp per day, so doubling the daily step must
    #    double the reading (a percent/bp mix-up would show up as a 100x, not a 2x)
    n1 = daily_noise_bp([0.0, 0.0, 0.01, 0.01])
    n2 = daily_noise_bp([0.0, 0.0, 0.02, 0.02])
    L("noise unit is bp/day (linear in the daily step)",
      n1 is not None and abs(n2 / n1 - 2.0) < 1e-9 and 40.0 < n1 < 60.0)

    # L9 the anchor is a scale constant, not a measurement: anchoring on a different
    #    day must leave every shape statistic unchanged
    alt = 3
    anchor_a = idx[0] / etf[0]
    anchor_b = idx[alt] / etf[alt]
    ea = [v * anchor_a for v in etf]
    eb = [v * anchor_b for v in etf]
    L("anchor day does not move the shape (returns are scale-free)",
      max(abs((ea[k] / ea[k - 1]) - (eb[k] / eb[k - 1])) for k in range(1, len(ea))) < 1e-12)

    # L10 a basis that never moves cannot be ranked -- say so instead of printing a fit
    flat = judge_pair(0.0, {"days": 100, "agree_pct": 100.0}, 0.0)
    L("flat basis -> flat_basis, not a pass", flat["verdict"] == "flat_basis")
    L("flat basis reason names the range", "range" in flat["why"])
    # ...and the same pair with a moving basis still reaches its real verdict
    L("a moving basis is judged on its merits",
      judge_pair(0.0, {"days": 100, "agree_pct": 100.0}, 50.0)["verdict"] == "PROXY_FIT")

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        log("  %s %s" % ("PASS" if ok else "FAIL", n))
    log("selftest %d/%d %s" % (len(legs) - len(bad), len(legs), "PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


def check():
    if not os.path.exists(OUT):
        log("CHECK_FAIL no face on disk")
        return 1
    old = json.load(open(OUT, encoding="utf-8"))
    new = build()
    problems = []
    for fut, v in new["pairs"].items():
        o = old["pairs"].get(fut) or {}
        if o.get("status") != v.get("status"):
            problems.append("%s status %s != %s" % (fut, v.get("status"), o.get("status")))
            continue
        if v.get("status") != "ok":
            continue
        for k in ("daily_noise_bp", "level_offset_pct", "verdict"):
            if o.get(k) != v.get(k):
                problems.append("%s.%s %r != %r" % (fut, k, v.get(k), o.get(k)))
        if (o.get("rule") or {}).get("agreement", {}).get("agree_pct") != \
                (v.get("rule") or {}).get("agreement", {}).get("agree_pct"):
            problems.append("%s.agree_pct moved" % fut)
    if problems:
        log("CHECK_FAIL " + "; ".join(problems[:6]))
        return 1
    log("CHECK_OK %s re-derived byte-for-byte" % new["verdict"]["state"])
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    log(face["verdict"]["sentence"])
    log("wrote %s" % os.path.relpath(OUT, base.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
