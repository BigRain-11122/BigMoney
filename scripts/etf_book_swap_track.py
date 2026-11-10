"""ETF book -- the swap's tracking difference is a number, not a disclaimer.

Three faces already say the same sentence in their own words: "a swap is a different ISIN
holding the same index -- tracking difference, fee, size and quotation width are NOT priced
here" (swap stack r1467, sibling entry, exec delta r1455). Written three times it is no longer
a caveat; it is an unpriced term of a trade this book has already executed. r1522 priced the
way out, r1523 measured the way back, r1524 paired the two, r1525 turned the discount into
shares. None of them answers the question a holder of the cheap sibling actually has:

    once I am carrying the sibling instead of the ticker I sold, what does it cost me per
    year, and how much more of one single fund am I carrying?

Neither question is a gap reading. The gap face reads a LEVEL (how wide is the gap today);
this reads the pair's own relative price PATH -- the daily change of the reconstruction the
gap face already publishes (imported, never rebuilt):

  1. DRIFT. mean daily change x BARS_PER_YEAR = pp/yr, priced on the notional that actually
     traded. The standard error is Newey-West, because premium changes are autocorrelated and
     the iid error prints a t that is far too confident. |t| < 2 is NOT_DISTINGUISHABLE_FROM_
     ZERO -- never "no cost".
  2. POWER. A reader is entitled to know whether the question is pending or unanswerable here:
     years of this sample needed to resolve a fee-scale drift (0.5 pp/yr) at 80% power and a
     two-sided 5% test. z and the trading-year length are imported from etf_book_forward, the
     face that owns that caliber.
  3. CONCENTRATION. The swap merged two legs into ONE ticker at ~40% of the risk book, and the
     ticket answers that with "the baskets are unchanged" -- true at basket level, silent at
     fund level. The difference between holding B at w1+w2 and holding A1 at w1 plus A2 at w2
     is w1*(dev_B - dev_A1) + w2*(dev_B - dev_A2); its scale is measured from the two relative
     series and their correlation, then priced. That is a reading, not an opinion.

The scaling is measured, not assumed. The pair's relative price is mean-reverting (the variance
ratio collapses from 1 at one session to ~0.2 at 120), so sqrt(BARS_PER_YEAR) * daily sd would
overstate a year by more than 2x. The headline noise uses the 120-session variance ratio; the
iid figure is printed beside it as an upper bound, and the whole VR curve goes into the payload
so the reader can see how far the assumption would have been off.

Usage:
    python scripts/etf_book_swap_track.py run
    python scripts/etf_book_swap_track.py --check
    python scripts/etf_book_swap_track.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap_face        # noqa: E402  (the one gap reconstruction)
import etf_book_swap_convergence as conv_face  # noqa: E402  (which SELL was a swap)
import etf_book_forward as fwd_face            # noqa: E402  (the trading year and the power z)

GAP_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")
STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_track.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_track.md")

BARS_PER_YEAR = fwd_face.BARS_PER_YEAR   # the repo's trading-year convention, not a local 252
POWER_Z = fwd_face.POWER_Z               # 80% power, two-sided 5%
NW_LAG = 5                               # premium changes are autocorrelated up to about a week
VR_HORIZONS = (5, 20, 60, 120)           # variance ratios published at all four
VR_REFERENCE = 120                       # the horizon the headline noise is scaled on
T_REJECT = 2.0                           # |t| below this is "not distinguishable", never "zero"
FEE_SCALE_PP = 0.5                       # a share-class fee difference, per year
BIG_SCALE_PP = 3.0                       # a drift the desk would actually care about
MIN_SESSIONS = 120                       # below this a variance ratio is noise about noise
CENT = 0.01

CAVEATS = [
    "the drift is a PRICE drift: it contains the two funds' premium changes as well as their "
    "fees and tracking, and this book has no NAV panel to split the two -- it is what a holder "
    "of the sibling actually experiences, not a fee estimate",
    "the reconstruction inherits the sibling-gap face's single IOPV anchor; changes cancel that "
    "offset, so the drift and the noise are identified even though the level is not",
    "the noise is scaled on the 120-session variance ratio because the relative price mean "
    "reverts; the iid figure beside it is an upper bound, and neither is a forecast -- beyond "
    "120 sessions this sample cannot estimate the ratio at all",
    "an unmeasurable leg is refused with a reason, never scored as zero drift and never scored "
    "as zero noise (r1230 family)",
    "the concentration block prices the DIFFERENCE between one fund and two; it says nothing "
    "about either fund's tracking against its index, which needs NAV",
]


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _refuse(face, why):
    face["verdict"] = "CANNOT_MEASURE"
    face["sentence"] = "这一问答不了：%s。" % why
    face["refused"] = why
    return face


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def daily_changes(rec):
    """The pair's relative price change per session, in pp. The anchor offset cancels."""
    return [rec[i] - rec[i - 1] for i in range(1, len(rec))]


def nw_se(x, lag=NW_LAG):
    """Newey-West standard error of the MEAN. Returns None when it cannot be estimated."""
    n = len(x)
    if n < 3:
        return None
    m = statistics.fmean(x)
    e = [v - m for v in x]
    var = sum(v * v for v in e) / n
    total = var
    for k in range(1, min(lag, n - 1) + 1):
        gk = sum(e[i] * e[i - k] for i in range(k, n)) / n
        total += 2.0 * (1.0 - k / (lag + 1.0)) * gk
    if total <= 0:
        return None
    return math.sqrt(total / n)


def variance_ratio(changes, k):
    """Overlapping VR(k) = Var(k-sum)/(k*Var(1)). Below 1 means mean reversion."""
    n = len(changes)
    if n <= k + 1:
        return None
    base = statistics.pvariance(changes)
    if base <= 0:
        return None
    sums = [sum(changes[i:i + k]) for i in range(0, n - k + 1)]
    if not sums:
        return None
    return statistics.pvariance(sums) / (k * base)


def power_years(sigma_pp, effect_pp):
    """Years of this sample needed to resolve `effect_pp` at 80% power, two-sided 5%."""
    if sigma_pp is None or not effect_pp:
        return None
    return (POWER_Z * float(sigma_pp) / float(effect_pp)) ** 2


def measure_pair(pair, changes, notional):
    """One leg: drift with a NW error, the variance-ratio curve, and the noise both ways."""
    row = {"leg_symbol": str(pair.get("leg_symbol")),
           "sibling_symbol": pair.get("sibling_symbol"),
           "gap_today_pp": _num(pair.get("gap_today_pp")),
           "sessions": len(changes or []),
           "notional_cny": None if notional is None else round(float(notional), 2),
           "mean_daily_pp": None, "drift_pp_per_year": None, "se_pp_per_year": None,
           "t_stat": None, "drift_cny_per_year": None, "se_cny_per_year": None,
           "noise_iid_pp_per_year": None, "noise_scaled_pp_per_year": None,
           "vr": {}, "verdict": None, "why": ""}
    if not changes or len(changes) < MIN_SESSIONS:
        row["verdict"] = "CANNOT_MEASURE"
        row["why"] = ("共同交易日只有 %d 根（门槛 %d）：漂移和方差比在这个样本上都是噪声"
                      % (len(changes or []), MIN_SESSIONS))
        return row
    n = len(changes)
    mean_d = statistics.fmean(changes)
    sd_d = statistics.stdev(changes)
    # every downstream figure is built from the PUBLISHED rounding, so the sheet and the
    # machine face cannot disagree in the last cent
    drift = round(mean_d * BARS_PER_YEAR, 4)
    se = nw_se(changes)
    se_year = None if se is None else round(se * BARS_PER_YEAR, 4)
    row["mean_daily_pp"] = round(mean_d, 6)
    row["drift_pp_per_year"] = drift
    row["noise_iid_pp_per_year"] = round(sd_d * math.sqrt(BARS_PER_YEAR), 3)
    for k in VR_HORIZONS:
        vr = variance_ratio(changes, k)
        row["vr"]["k%d" % k] = None if vr is None else round(vr, 3)
    vr_ref = row["vr"].get("k%d" % VR_REFERENCE)
    if vr_ref is not None and vr_ref > 0:
        row["noise_scaled_pp_per_year"] = round(
            sd_d * math.sqrt(BARS_PER_YEAR) * math.sqrt(vr_ref), 3)
    if se_year is None or se_year <= 0:
        row["verdict"] = "CANNOT_MEASURE"
        row["why"] = "标准误估不出来：这一腿的漂移没有误差带，印出来就是假装精确"
        return row
    t = drift / se_year
    row["se_pp_per_year"] = round(se_year, 4)
    row["t_stat"] = round(t, 3)
    if row["notional_cny"] is not None:
        row["drift_cny_per_year"] = round(row["notional_cny"] * drift / 100.0, 2)
        row["se_cny_per_year"] = round(row["notional_cny"] * se_year / 100.0, 2)
    if abs(t) < T_REJECT:
        row["verdict"] = "NOT_DISTINGUISHABLE_FROM_ZERO"
        row["why"] = ("点估计 %+.2f pp/年，但一年标准误 %.2f pp 把它盖过去了（t=%+.2f）："
                      "这个样本分不开「兄弟票每年贵几个 pp」与「没差别」"
                      % (drift, se_year, t))
    elif drift > 0:
        row["verdict"] = "HOLDING_THE_SIBLING_LOSES"
        row["why"] = ("换出去的票在这段历史里相对变贵了 %+.2f pp/年（t=%+.2f）："
                      "拿着兄弟票这一边是让出" % (drift, t))
    else:
        row["verdict"] = "HOLDING_THE_SIBLING_GAINS"
        row["why"] = ("换出去的票在这段历史里相对变便宜了 %+.2f pp/年（t=%+.2f）："
                      "拿着兄弟票这一边是赚到" % (drift, t))
    return row


def _correlation(a, b):
    if len(a) < 3 or len(a) != len(b):
        return None
    try:
        return statistics.correlation(a, b)
    except (statistics.StatisticsError, ValueError):
        return None


def merge_block(series, rows, stack):
    """Two legs in one fund vs the same money in two funds: the measured difference."""
    block = {"sibling_symbol": None, "legs": {}, "correlation": None,
             "weight_before": {}, "weight_after": None, "weight_sum_before": None,
             "invested_cny": None, "sigma_diff_pp_per_year": None,
             "sigma_diff_cny_per_year": None, "iid_upper_bound_pp": None,
             "sentence": "", "verdict": "NOT_MEASURED", "why": ""}
    rb_before = _num((stack or {}).get("risk_book_before_cny"))
    widest = (stack or {}).get("widest_name") or {}
    if rb_before is None or rb_before <= 0:
        block["why"] = "净额单面没有换票前的风险腿：权重没有分母"
        return block
    priced = [r for r in rows
              if r.get("drift_pp_per_year") is not None
              and r.get("noise_scaled_pp_per_year") is not None]
    pairs = []
    for r in priced:
        leg = r["leg_symbol"]
        act = conv_face.executed_notional(stack, leg)
        amount = _num((act or {}).get("amount_cny"))
        if amount is None or amount <= 0:
            continue
        pairs.append((leg, amount / rb_before, r))
    if len(pairs) < 2:
        block["why"] = ("能定价的换票腿只有 %d 条：并成一只这件事至少要两条腿才问得出来"
                        % len(pairs))
        return block
    # align the two relative series on the sessions both legs traded
    keys = [p[0] for p in pairs]
    a, b = series.get(keys[0]) or {}, series.get(keys[1]) or {}
    common = sorted(set(a) & set(b))
    if len(common) < MIN_SESSIONS:
        block["why"] = ("两条腿共同的交易日只有 %d 根：相关系数估不出来，合并风险就是一个假设"
                        % len(common))
        return block
    corr = _correlation([a[d] for d in common], [b[d] for d in common])
    if corr is None:
        block["why"] = "两条腿的相对变化算不出相关系数"
        return block
    (l1, w1, r1), (l2, w2, r2) = pairs[0], pairs[1]
    s1 = float(r1["noise_scaled_pp_per_year"])
    s2 = float(r2["noise_scaled_pp_per_year"])
    var = (w1 * w1 * s1 * s1 + w2 * w2 * s2 * s2 + 2.0 * w1 * w2 * corr * s1 * s2)
    if var <= 0:
        block["why"] = "两份特有波动在相关系数下相消为负：不是可解释的读数"
        return block
    sigma = round(math.sqrt(var), 4)
    invested = round((w1 + w2) * rb_before, 2)
    iid1 = float(r1["noise_iid_pp_per_year"])
    iid2 = float(r2["noise_iid_pp_per_year"])
    iid_var = (w1 * w1 * iid1 * iid1 + w2 * w2 * iid2 * iid2
               + 2.0 * w1 * w2 * corr * iid1 * iid2)
    sib = widest.get("symbol") or r1.get("sibling_symbol") or r2.get("sibling_symbol") or "?"
    block.update({
        "sibling_symbol": sib,
        "legs": {l1: {"weight": round(w1, 6), "sigma_pp": s1},
                 l2: {"weight": round(w2, 6), "sigma_pp": s2}},
        "correlation": round(corr, 4),
        "weight_before": {l1: round(w1, 6), l2: round(w2, 6)},
        "weight_sum_before": round(w1 + w2, 6),
        "weight_after": _num(widest.get("share_of_risk_book")),
        "invested_cny": round(invested, 2),
        "sigma_diff_pp_per_year": round(sigma, 4),
        "sigma_diff_cny_per_year": round(invested * sigma / 100.0, 2),
        "iid_upper_bound_pp": round(math.sqrt(iid_var), 4),
        "verdict": "MERGED_INTO_ONE_FUND",
        "sentence": ("把 %s 与 %s 并成一只 %s 之后，风险腿里这一块从两只各 %.1f%% 变成一只 %.1f%%；"
                     "两种拿法的**特有**波动差 %.2f pp/年（占风险腿），在 %s 上是 %s/年"
                     % (l1, l2, sib, w1 * 100, (w1 + w2) * 100,
                        sigma, _money(invested), _money_y(invested * sigma / 100.0))),
    })
    return block


def _money(v):
    if v is None:
        return "—"
    return "¥%s" % format(float(v), ",.2f")


def _money_y(v):
    if v is None:
        return "—"
    return "¥%s" % format(float(v), ",.0f")


def _pp(v, nd=2, signed=True):
    """A signed reading for a difference; a magnitude (a noise) never carries a plus."""
    if v is None:
        return "—"
    if signed:
        return "%+.*f pp" % (nd, float(v))
    return "%.*f pp" % (nd, float(v))


def _load_series(pair):
    """(dates, changes_by_date) for one published pair, or (None, reason)."""
    files = pair.get("daily_files") or []
    if len(files) != 2 or not all(files):
        return None, "这一对没有本地日线面板"
    try:
        a = gap_face.load_close(os.path.join(ROOT, files[0]))
        b = gap_face.load_close(os.path.join(ROOT, files[1]))
    except OSError as exc:
        return None, "面板读不出：%r" % (exc,)
    dates, ca, cb = gap_face.common_series(a, b)
    if len(dates) < 2:
        return None, "共同交易日不足两根"
    rec, _offset = gap_face.reconstruct(gap_face.gap_series(ca, cb), pair.get("gap_today_pp"))
    if not rec:
        return None, "价差重建是空的"
    changes = daily_changes(rec)
    return dict(zip(dates[1:], changes)), None


def _measure(ctx):
    as_of = ctx.get("as_of")
    face = {"artifact": "etf_book_swap_track", "bar": as_of, "evidence_cutoff": as_of,
            "verdict": None, "rows": [], "skipped": [], "merge": None, "sentence": "",
            "refused": None, "bars_per_year": BARS_PER_YEAR, "power_z": POWER_Z,
            "vr_horizons": list(VR_HORIZONS), "vr_reference": VR_REFERENCE,
            "nw_lag": NW_LAG, "t_reject": T_REJECT, "min_sessions": MIN_SESSIONS,
            "fee_scale_pp": FEE_SCALE_PP, "big_scale_pp": BIG_SCALE_PP,
            "sources": {"sibling_gap": "results/etf_book_sibling_gap.json",
                        "swap_stack": "results/etf_book_swap_stack.json"},
            "caveats": list(CAVEATS)}
    gap = ctx.get("sibling_gap")
    stack = ctx.get("swap_stack")
    if not gap:
        return _refuse(face, "没有已发布的价差面（scripts/etf_book_sibling_gap.py run）")
    if not stack:
        return _refuse(face, "没有已发布的净额单面：不知道这张单动了多少钱")
    stack_bar = stack.get("asof") or stack.get("bar")
    if as_of and stack_bar and str(stack_bar) != str(as_of):
        return _refuse(face, "净额单面停在 %s、这张单是 %s：不同 bar 的两条腿不能并排"
                       % (stack_bar, as_of))
    gap_session = gap.get("session")
    # The gap face's session is DISCLOSED, never a blocker: the reconstruction's offset pins
    # the LEVEL, and every change here cancels it, so a two-session-old anchor still yields
    # exact changes. Refusing on it would be refusing a number that is right.
    face["anchor_session"] = gap_session
    face["anchor_behind_bar"] = bool(as_of and gap_session and str(gap_session) != str(as_of))

    override = ctx.get("series")
    rows, skipped, series = [], [], {}
    for pair in gap.get("pairs") or []:
        leg = str(pair.get("leg_symbol"))
        act = conv_face.executed_notional(stack, leg)
        if act is None:
            skipped.append({"leg_symbol": leg, "sibling_symbol": pair.get("sibling_symbol"),
                            "why": "这张单没有换出这只票：它的漂移不是这笔交易的成本"})
            continue
        if override is not None:
            changes, why = override.get(leg), None if override.get(leg) is not None else "夹具没有这一腿"
        else:
            changes, why = _load_series(pair)
        if changes is None:
            rows.append({"leg_symbol": leg, "sibling_symbol": pair.get("sibling_symbol"),
                         "verdict": "CANNOT_MEASURE", "why": why, "sessions": 0,
                         "notional_cny": round(float(act.get("amount_cny") or 0.0), 2),
                         "vr": {}, "drift_pp_per_year": None,
                         "noise_scaled_pp_per_year": None})
            continue
        series[leg] = changes
        rows.append(measure_pair(pair, list(changes.values()) if isinstance(changes, dict) else changes,
                                 act.get("amount_cny")))
    face["rows"] = rows
    if skipped:
        face["skipped"] = skipped

    priced = [r for r in rows if r.get("t_stat") is not None]
    if not priced:
        face["verdict"] = "NOTHING_MEASURED"
        face["sentence"] = ("这一单没有可测量的换票：换出的票没有足够的共同历史——"
                            "这不是「跟踪差为零」的结论。")
        return face
    face["merge"] = merge_block(series, rows, stack)

    notional = sum(float(r.get("notional_cny") or 0.0) for r in priced)
    drift_cny = sum(float(r.get("drift_cny_per_year") or 0.0) for r in priced)
    se_cny = sum(float(r.get("se_cny_per_year") or 0.0) for r in priced)
    face["totals"] = {"measured_legs": len(priced), "sessions_min": min(r["sessions"] for r in priced),
                      "notional_cny": round(notional, 2),
                      "drift_cny_per_year": round(drift_cny, 2),
                      "se_cny_per_year": round(se_cny, 2),
                      "losing_legs": sum(1 for r in priced
                                         if r["verdict"] == "HOLDING_THE_SIBLING_LOSES"),
                      "gaining_legs": sum(1 for r in priced
                                          if r["verdict"] == "HOLDING_THE_SIBLING_GAINS"),
                      "undistinguishable_legs": sum(
                          1 for r in priced if r["verdict"] == "NOT_DISTINGUISHABLE_FROM_ZERO")}
    if face["totals"]["losing_legs"]:
        face["verdict"] = "SIBLING_LOSES_PER_YEAR"
    elif face["totals"]["gaining_legs"]:
        face["verdict"] = "SIBLING_GAINS_PER_YEAR"
    else:
        face["verdict"] = "DRIFT_NOT_DISTINGUISHABLE_FROM_ZERO"
    face["sentence"] = sentence(face)
    return face


def compute(ctx):
    """Load the two published faces and the panels, then measure. Nothing is re-reconciled."""
    return _measure(ctx)


def sentence(face):
    rows = [r for r in face.get("rows") or [] if r.get("t_stat") is not None]
    if not rows:
        return face.get("sentence") or "这一问答不了。"
    parts = []
    for r in rows:
        parts.append("%s→%s 漂移 %s（t=%+.2f，一年标准误 %s，%s）"
                     % (r["leg_symbol"], r.get("sibling_symbol") or "?",
                        _pp(r["drift_pp_per_year"]), float(r["t_stat"]),
                        _pp(r["se_pp_per_year"]),
                        "方向是拿着兄弟票让出" if (r["drift_pp_per_year"] or 0) > 0
                        else "方向是拿着兄弟票赚到"))
    t = face.get("totals") or {}
    head = ("三张面都写着「跟踪差没有定价」。这一面把它定成了两个数：%s；合计 %s/年，"
            "两条腿合起来的一年标准误 %s——"
            % ("；".join(parts), _money_y(t.get("drift_cny_per_year")),
               _money_y(t.get("se_cny_per_year"))))
    if face.get("verdict") == "DRIFT_NOT_DISTINGUISHABLE_FROM_ZERO":
        head += "点估计是站在「继续变贵」这一边，但标准误把它盖过去了，判**量不出来**（不是「没有成本」）。"
    else:
        head += "判决 **%s**。" % face["verdict"]
    m = face.get("merge") or {}
    if m.get("sigma_diff_pp_per_year") is not None:
        years_fee = power_years(max(r["noise_scaled_pp_per_year"] or 0.0 for r in rows), FEE_SCALE_PP)
        head += ("并成一只之后，单一基金特有波动多担 %.2f pp/年（占风险腿；%s/年），"
                 "而这张单省下的是入场折扣 ¥9,761.8——一个是一次性的价，一个是每年都在的波动。"
                 % (m["sigma_diff_pp_per_year"], _money_y(m.get("sigma_diff_cny_per_year"))))
        if years_fee is not None:
            head += ("要分辨一条 0.5 pp/年的费率差，这个样本需要 %.0f 年：这正是它答不了的题。"
                     % years_fee)
    return head


def md_lines(face, heading="## 换到兄弟票之后，每年贵多少、又多担多少（r1526）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的跟踪差面（跑 "
                "scripts/etf_book_swap_track.py run）。缺面不等于跟踪差为零。", ""]
    if face.get("refused"):
        return ["", heading, "- **量不出来**：%s。" % face["refused"],
                "- 读法：这一节量的是「拿着兄弟票而不是我卖掉的那只」每年差多少；"
                "「量不出来」与「差为零」是两件事。", ""]
    L = ["", heading, "- %s" % (face.get("sentence") or "")]
    rows = [r for r in face.get("rows") or [] if r.get("t_stat") is not None]
    if rows:
        L += ["", "| 换出 | 换入 | 共同交易日 | 漂移/年 | t | 一年标准误 | 漂移金额/年 | "
                  "特有噪声(iid) | 特有噪声(实测) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| %s | %s | %d | %s | %+.2f | %s | %s | %s | **%s** |"
                     % (r["leg_symbol"], r.get("sibling_symbol") or "?", r["sessions"],
                        _pp(r["drift_pp_per_year"]), float(r["t_stat"]),
                        _pp(r["se_pp_per_year"]), _money_y(r.get("drift_cny_per_year")),
                        _pp(r.get("noise_iid_pp_per_year"), 1, False),
                        _pp(r.get("noise_scaled_pp_per_year"), 1, False)))
        t = face.get("totals") or {}
        L += ["", "合计：动 %s，漂移点估计 **%s/年**，两条腿合起来的标准误 %s/年（样本 %d 个共同交易日）。"
                  % (_money_y(t.get("notional_cny")), _money_y(t.get("drift_cny_per_year")),
                     _money_y(t.get("se_cny_per_year")), t.get("sessions_min") or 0),
              "", "- **漂移是价格口径**：它把两只基金的**溢价变动**和**费率/跟踪**加在一起，"
                  "这本书没有 NAV 面板拆不开——这就是拿着兄弟票实际经历的那个数，不是费率估计。",
              "- **噪声为什么要按实测缩放**：这对票的相对价格是均值回复的，"
              "方差比从 1 根 bar 的 1.0 掉到 %d 根的 %s，所以用 √%d×日波动会把一年的噪声高估 %.1f 倍；"
              "iid 那一列印出来当上界，不是主读数。"
                  % (face.get("vr_reference") or VR_REFERENCE,
                     "%.2f" % (rows[0]["vr"].get("k%d" % (face.get("vr_reference") or VR_REFERENCE))
                               or 0.0),
                     int(face.get("bars_per_year") or BARS_PER_YEAR),
                     1.0 / max(math.sqrt(rows[0]["vr"].get("k%d" % (face.get("vr_reference")
                                                                   or VR_REFERENCE)) or 1.0), 1e-9))]
    else:
        L.append("- 这一单没有可测量的换票；这不是「跟踪差为零」的结论。")
    m = face.get("merge") or {}
    if m.get("sigma_diff_pp_per_year") is not None:
        L += ["", "**并成一只之后多担的那部分**：%s" % (m.get("sentence") or ""),
              "", "| 腿 | 换票前权重（风险腿） | 特有波动/年 |",
              "|---|---|---|"]
        for leg, info in (m.get("legs") or {}).items():
            L.append("| %s | %.2f%% | %s |"
                     % (leg, float(info["weight"]) * 100, _pp(info["sigma_pp"], 2, False)))
        L += ["| 合并后 | %.2f%% | — |" % (float(m.get("weight_after") or 0.0) * 100),
              "", "- 两种拿法的**特有**波动差 **%s/年**（占风险腿）= %s/年，"
                  "两条腿相对变化的相关系数 %.3f；iid 口径那里会印成 %s/年（上界）。"
                  % (_pp(m.get("sigma_diff_pp_per_year")), _money_y(m.get("sigma_diff_cny_per_year")),
                     float(m.get("correlation") or 0.0), _pp(m.get("iid_upper_bound_pp"), 2, False)),
              "- 票面另一节说「篮子没变」，那是在**篮子**维度上说的，成立；"
              "这一节说的是**基金**维度：并成一只之后，这 %s 的仓位现在是押在一只票上，"
              "不是押在两只上——这两句话都要读。"
              % _money_y(m.get("invested_cny"))]
    else:
        L.append("- 合并风险这一块没记：%s。" % (m.get("why") or "无"))
    L += ["", "- 判读：这一面量的是**持有**的年度差与**合并**的特有波动；"
              "r1522 的往返过路费是一次性的，r1525 的份数是一次性的入场价——"
              "三者单位不同，不能相加。"]
    if face.get("anchor_behind_bar"):
        L.append("- **上游锚比这张单旧**：换票面的价差锚停在 %s，这张单是 %s。"
                 "漂移/噪声不受影响（变化抵消了锚的偏移），但「今日价差有多宽」那几节读的是旧 bar——"
                 "系列面不在 S6 自动重算链里，它只被 check，不会被 run。"
                 % (face.get("anchor_session"), face.get("bar")))
    return L


def check(face):
    """Re-derive every claim the payload makes. A refusal is not a failure."""
    problems = []
    if not face:
        return ["no face"]
    if face.get("refused"):
        return problems
    bp = float(face.get("bars_per_year") or BARS_PER_YEAR)
    for r in face.get("rows") or []:
        leg = r.get("leg_symbol")
        if r.get("verdict") == "CANNOT_MEASURE":
            if r.get("drift_pp_per_year") is not None:
                problems.append("%s refused but carries a drift" % leg)
            continue
        if r.get("sessions") is None or r["sessions"] < int(face.get("min_sessions") or MIN_SESSIONS):
            problems.append("%s priced on %s sessions" % (leg, r.get("sessions")))
        want = round(float(r["mean_daily_pp"]) * bp, 4)
        if abs(want - float(r["drift_pp_per_year"])) > 1e-3:
            problems.append("%s drift %s != mean*%s" % (leg, r["drift_pp_per_year"], bp))
        if r.get("se_pp_per_year"):
            t = float(r["drift_pp_per_year"]) / float(r["se_pp_per_year"])
            if abs(t - float(r["t_stat"])) > 2e-3:
                problems.append("%s t %.4f != drift/se %.4f" % (leg, r["t_stat"], t))
        if r.get("drift_cny_per_year") is not None and r.get("notional_cny"):
            want_cny = round(float(r["notional_cny"]) * float(r["drift_pp_per_year"]) / 100.0, 2)
            if abs(want_cny - float(r["drift_cny_per_year"])) > CENT:
                problems.append("%s drift CNY %s != notional*pp/100 %s"
                                % (leg, r["drift_cny_per_year"], want_cny))
        vr_ref = (r.get("vr") or {}).get("k%d" % int(face.get("vr_reference") or VR_REFERENCE))
        if vr_ref and r.get("noise_scaled_pp_per_year") is not None:
            want_noise = round(float(r["noise_iid_pp_per_year"]) * math.sqrt(float(vr_ref)), 3)
            if abs(want_noise - float(r["noise_scaled_pp_per_year"])) > 5e-3:
                problems.append("%s scaled noise %s != iid*sqrt(VR) %s"
                                % (leg, r["noise_scaled_pp_per_year"], want_noise))
        tval = float(r["t_stat"])
        v = r.get("verdict")
        if abs(tval) < float(face.get("t_reject") or T_REJECT):
            if v != "NOT_DISTINGUISHABLE_FROM_ZERO":
                problems.append("%s |t|=%+.2f but verdict %s" % (leg, tval, v))
        elif float(r["drift_pp_per_year"]) > 0 and v != "HOLDING_THE_SIBLING_LOSES":
            problems.append("%s positive drift with |t|>=2 but verdict %s" % (leg, v))
        elif float(r["drift_pp_per_year"]) < 0 and v != "HOLDING_THE_SIBLING_GAINS":
            problems.append("%s negative drift with |t|>=2 but verdict %s" % (leg, v))
    m = face.get("merge") or {}
    if m.get("sigma_diff_pp_per_year") is not None:
        legs = m.get("legs") or {}
        if len(legs) != 2:
            problems.append("merge priced on %d legs" % len(legs))
        else:
            (a, ia), (b, ib) = list(legs.items())
            w1, w2 = float(ia["weight"]), float(ib["weight"])
            s1, s2 = float(ia["sigma_pp"]), float(ib["sigma_pp"])
            rho = float(m["correlation"])
            if not -1.0 <= rho <= 1.0:
                problems.append("correlation %r is not a correlation" % rho)
            var = w1 * w1 * s1 * s1 + w2 * w2 * s2 * s2 + 2.0 * w1 * w2 * rho * s1 * s2
            if var <= 0:
                problems.append("merge variance is not positive")
            else:
                if abs(math.sqrt(var) - float(m["sigma_diff_pp_per_year"])) > 5e-3:
                    problems.append("merge sigma %s != closed form %.4f"
                                    % (m["sigma_diff_pp_per_year"], math.sqrt(var)))
                if m.get("invested_cny") and m.get("sigma_diff_cny_per_year") is not None:
                    want = round(float(m["invested_cny"])
                                 * round(math.sqrt(var), 4) / 100.0, 2)
                    if abs(want - float(m["sigma_diff_cny_per_year"])) > CENT:
                        problems.append("merge CNY %s != invested*sigma/100 %s"
                                        % (m["sigma_diff_cny_per_year"], want))
            if float(m.get("iid_upper_bound_pp") or 0.0) + 1e-9 < float(m["sigma_diff_pp_per_year"]):
                problems.append("iid upper bound is below the scaled reading")
    tot = face.get("totals") or {}
    if tot:
        priced = [r for r in face.get("rows") or [] if r.get("t_stat") is not None]
        if tot.get("measured_legs") != len(priced):
            problems.append("measured_legs %s != rows with t %d"
                            % (tot.get("measured_legs"), len(priced)))
        want = round(sum(float(r.get("drift_cny_per_year") or 0.0) for r in priced), 2)
        if abs(want - float(tot.get("drift_cny_per_year") or 0.0)) > CENT:
            problems.append("total drift CNY %s != sum of legs %s"
                            % (tot.get("drift_cny_per_year"), want))
    return problems


# ------------------------------------------------------------------ selftest fixtures

def _synth(n, drift, noise_sd, seed, phi=0.0, exact=False):
    """A relative-change series with a known daily drift and an AR(1) noise term.

    `exact` removes the sample mean of the noise, so a fixture's drift is the drift it is
    designed with rather than a draw around it.
    """
    rng = __import__("random").Random(seed)
    noise, prev = [], 0.0
    for _ in range(n):
        eps = rng.gauss(0.0, noise_sd)
        prev = phi * prev + eps if phi else eps
        noise.append(prev)
    if exact and noise:
        m = statistics.fmean(noise)
        noise = [v - m for v in noise]
    return [drift + v for v in noise]


def _fixture(legs=None, sessions=600):
    legs = legs or {"159501": 0.05, "513100": 0.04}
    stack = {"asof": "2026-11-10",
             "risk_book_before_cny": 392535.9,
             "risk_book_after_cny": 392404.9,
             "widest_name": {"symbol": "159513", "share_of_risk_book": 0.3996},
             "actions": [
                 {"side": "SELL", "symbol": "159501", "lots": 372, "price": 2.11,
                  "amount_cny": 78492.0,
                  "why": "swap 159501 -> 159513 (r1466 verdict WINDOW_ALWAYS_OPEN)"},
                 {"side": "SELL", "symbol": "513100", "lots": 355, "price": 2.21,
                  "amount_cny": 78455.0,
                  "why": "swap 513100 -> 159513 (r1466 verdict WINDOW_ALWAYS_OPEN)"},
                 {"side": "BUY", "symbol": "159513", "lots": 891, "price": 1.76,
                  "amount_cny": 156816.0, "why": "merged buy for 159501 + 513100"}]}
    gap = {"session": "2026-11-10",
           "pairs": [{"leg_symbol": "159501", "sibling_symbol": "159513",
                      "gap_today_pp": 8.6708, "daily_files": ["a.csv", "b.csv"]},
                     {"leg_symbol": "513100", "sibling_symbol": "159513",
                      "gap_today_pp": 6.2867, "daily_files": ["c.csv", "d.csv"]},
                     {"leg_symbol": "159577", "sibling_symbol": "513850",
                      "gap_today_pp": 0.1903, "daily_files": ["e.csv", "f.csv"]}]}
    series = {}
    for leg, drift in legs.items():
        if drift is None:
            continue
        seed = sum(ord(c) for c in leg)
        series[leg] = {"2026-%04d" % i: v
                       for i, v in enumerate(_synth(sessions, drift, 0.10, seed, exact=True))}
    return {"as_of": "2026-11-10", "sibling_gap": gap, "swap_stack": stack, "series": series}


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    f = _measure(_fixture())
    priced = [r for r in f["rows"] if r.get("t_stat") is not None]
    leg("L1 both swapped legs are measured", len(priced) == 2, len(priced))
    leg("L2 the leg that was not swapped is skipped, not zeroed",
        [s["leg_symbol"] for s in f.get("skipped") or []] == ["159577"], f.get("skipped"))
    r = priced[0]
    leg("L3 drift = mean daily change x the repo's trading year",
        abs(float(r["mean_daily_pp"]) * BARS_PER_YEAR - float(r["drift_pp_per_year"])) < 1e-3, r)
    leg("L4 a large positive drift reads as holding the sibling loses",
        r["verdict"] == "HOLDING_THE_SIBLING_LOSES", r["verdict"])
    leg("L5 the dollars are the traded notional x the drift",
        abs(float(r["drift_cny_per_year"])
            - float(r["notional_cny"]) * float(r["drift_pp_per_year"]) / 100.0) < CENT,
        r["drift_cny_per_year"])
    leg("L6 the face verdict follows the legs", f["verdict"] == "SIBLING_LOSES_PER_YEAR", f["verdict"])
    leg("L7 the variance ratio is published at every horizon",
        set(r["vr"]) == {"k%d" % k for k in VR_HORIZONS}, r["vr"])
    leg("L8 scaled noise = iid x sqrt(VR_ref)",
        abs(float(r["noise_scaled_pp_per_year"])
            - float(r["noise_iid_pp_per_year"])
            * math.sqrt(float(r["vr"]["k%d" % VR_REFERENCE]))) < 5e-3, r["noise_scaled_pp_per_year"])
    leg("L9 check is clean on the clean face", check(f) == [], check(f))
    leg("L10 the sentence carries pp and money",
        "pp" in f["sentence"] and "¥" in f["sentence"], f["sentence"][:80])
    m = f["merge"]
    leg("L11 merge weights come from the traded amounts over the pre-swap risk book",
        abs(float(m["weight_before"]["159501"]) - 78492.0 / 392535.9) < 1e-6, m["weight_before"])
    leg("L12 merge sigma matches the closed form with the measured correlation",
        abs(math.sqrt(
            float(m["legs"]["159501"]["weight"]) ** 2 * float(m["legs"]["159501"]["sigma_pp"]) ** 2
            + float(m["legs"]["513100"]["weight"]) ** 2 * float(m["legs"]["513100"]["sigma_pp"]) ** 2
            + 2 * float(m["legs"]["159501"]["weight"]) * float(m["legs"]["513100"]["weight"])
            * float(m["correlation"]) * float(m["legs"]["159501"]["sigma_pp"])
            * float(m["legs"]["513100"]["sigma_pp"]))
            - float(m["sigma_diff_pp_per_year"])) < 5e-3, m["sigma_diff_pp_per_year"])
    leg("L13 the merge money is the invested amount x the sigma",
        abs(float(m["sigma_diff_cny_per_year"])
            - float(m["invested_cny"]) * float(m["sigma_diff_pp_per_year"]) / 100.0) < CENT,
        m["sigma_diff_cny_per_year"])

    # --- a flat leg cannot be called a cost -------------------------------------------
    flat = _measure(_fixture({"159501": 0.0, "513100": 0.0}, sessions=600))
    leg("L14 a zero drift with noise is not distinguishable, not zero cost",
        all(x["verdict"] == "NOT_DISTINGUISHABLE_FROM_ZERO"
            for x in flat["rows"] if x.get("t_stat") is not None),
        [(x["leg_symbol"], x["verdict"]) for x in flat["rows"]])
    leg("L15 the face verdict for that sample is not a cost",
        flat["verdict"] == "DRIFT_NOT_DISTINGUISHABLE_FROM_ZERO", flat["verdict"])

    # --- Newey-West vs iid on an autocorrelated series --------------------------------
    ar = _synth(600, 0.0, 0.35, 7, phi=0.6)
    iid = statistics.stdev(ar) / math.sqrt(len(ar))
    leg("L16 the NW error is larger than the iid error when changes are autocorrelated",
        nw_se(ar) > iid * 1.2, (nw_se(ar), iid))
    white = _synth(600, 0.0, 0.35, 11, phi=0.0)
    leg("L17 on white noise the two errors agree within 20%",
        abs(nw_se(white) - statistics.stdev(white) / math.sqrt(len(white)))
        < 0.2 * (statistics.stdev(white) / math.sqrt(len(white))),
        nw_se(white))

    # --- variance ratio measures the mean reversion ---------------------------------
    alternating = [(1.0 if i % 2 == 0 else -1.0) for i in range(600)]
    leg("L18 VR collapses on an alternating series (mean reversion is measured, not assumed)",
        variance_ratio(alternating, 20) < 0.2, variance_ratio(alternating, 20))
    leg("L19 VR is about 1 on white noise",
        abs(variance_ratio(white, 20) - 1.0) < 0.25, variance_ratio(white, 20))

    # --- power floor -----------------------------------------------------------------
    leg("L20 the power floor grows as the effect shrinks",
        power_years(3.0, FEE_SCALE_PP) > power_years(3.0, BIG_SCALE_PP) > 0,
        (power_years(3.0, FEE_SCALE_PP), power_years(3.0, BIG_SCALE_PP)))
    leg("L21 the power floor uses the imported z and trading year",
        abs(power_years(3.0, 1.0) - (POWER_Z * 3.0) ** 2) < 1e-9 and BARS_PER_YEAR == fwd_face.BARS_PER_YEAR,
        power_years(3.0, 1.0))

    # --- refusals --------------------------------------------------------------------
    short = _fixture({"159501": 0.01, "513100": 0.01}, sessions=60)
    fs = _measure(short)
    leg("L22 too few sessions is a refusal, not a zero",
        all(x.get("verdict") == "CANNOT_MEASURE" for x in fs["rows"]),
        [(x["leg_symbol"], x.get("verdict")) for x in fs["rows"]])
    leg("L23 a refused leg carries no drift", fs["verdict"] == "NOTHING_MEASURED", fs["verdict"])
    nopair = _fixture()
    nopair["series"] = {"159501": nopair["series"]["159501"]}
    fn = _measure(nopair)
    leg("L24 a missing panel is refused on the leg, not silently dropped",
        any(x.get("verdict") == "CANNOT_MEASURE" for x in fn["rows"]), fn["rows"])
    nogap = _fixture()
    nogap["sibling_gap"] = None
    leg("L25 no gap face refuses the whole face", _measure(nogap).get("refused") is not None)
    bar = _fixture()
    bar["as_of"] = "2026-11-09"
    leg("L26 a bar mismatch refuses rather than stitching two bars",
        _measure(bar).get("refused") is not None)

    # --- the anchor session is disclosed, never a blocker -----------------------------
    oldanchor = _fixture()
    oldanchor["sibling_gap"]["session"] = "2026-11-06"
    fo = _measure(oldanchor)
    leg("L27 an older gap anchor still measures, and says so",
        fo.get("verdict") != "CANNOT_MEASURE" and fo.get("anchor_behind_bar") is True
        and fo.get("anchor_session") == "2026-11-06",
        (fo.get("verdict"), fo.get("anchor_behind_bar")))
    leg("L28 that disclosure reaches the printed section",
        any("上游锚比这张单旧" in x for x in md_lines(fo)))

    # --- check() must catch tampering -----------------------------------------------
    bad = _measure(_fixture())
    bad["rows"][0]["drift_pp_per_year"] = float(bad["rows"][0]["drift_pp_per_year"]) + 0.5
    leg("L29 check catches a drift that is not mean x trading year", check(bad) != [])
    bad2 = _measure(_fixture())
    bad2["rows"][0]["t_stat"] = float(bad2["rows"][0]["t_stat"]) + 1.0
    leg("L30 check catches a t that disagrees with drift/se", check(bad2) != [])
    bad3 = _measure(_fixture())
    bad3["merge"]["sigma_diff_pp_per_year"] = float(bad3["merge"]["sigma_diff_pp_per_year"]) + 0.5
    leg("L31 check catches a merge sigma off the closed form", check(bad3) != [])
    bad4 = _measure(_fixture())
    bad4["rows"][0]["verdict"] = "NOT_DISTINGUISHABLE_FROM_ZERO"
    leg("L32 check catches a loss relabelled as indistinguishable", check(bad4) != [])
    bad5 = _measure(_fixture())
    bad5["totals"]["drift_cny_per_year"] = 1.0
    leg("L33 check catches a total that is not the sum of the legs", check(bad5) != [])

    # --- rendering -------------------------------------------------------------------
    leg("L34 an absent face prints a refusal line", any("跑 scripts" in x for x in md_lines(None)))
    leg("L35 a refused face still renders a line",
        any("量不出来" in x for x in md_lines(_measure(nogap))))
    rendered = "\n".join(md_lines(f))
    leg("L36 the section prints both annual cost and the merge block",
        "漂移" in rendered and "并成一只之后多担的那部分" in rendered, rendered[:120])
    leg("L37 the section says the three units cannot be added",
        "不能相加" in rendered)

    ok = sum(1 for _n, v, _d in legs if v)
    for n, v, d in legs:
        print("  %-6s %s%s" % ("PASS" if v else "FAIL", n, "" if v else "  :: %r" % (d,)))
    print("swap_track selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ------------------------------------------------------------------ entry points

def _emit(line):
    """Console-safe print: a GBK terminal must not be able to kill a published face."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "backslashreplace").decode("ascii"))


def run():
    gap = _read_json(GAP_JSON)
    stack = _read_json(STACK_FACE)
    as_of = (stack or {}).get("asof") or (gap or {}).get("session")
    face = compute({"as_of": as_of, "sibling_gap": gap, "swap_stack": stack})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    L = ["# 换到兄弟票之后，每年贵多少、又多担多少（r1526）", "",
         "bar %s ｜ 判定 **%s**" % (as_of, face["verdict"]), ""]
    L += md_lines(face, heading="## 逐腿读数")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    m = face.get("merge") or {}
    _emit(json.dumps({"verdict": face["verdict"],
                      "rows": len([r for r in face.get("rows") or [] if r.get("t_stat") is not None]),
                      "skipped": len(face.get("skipped") or []),
                      "drift_cny_per_year": (face.get("totals") or {}).get("drift_cny_per_year"),
                      "se_cny_per_year": (face.get("totals") or {}).get("se_cny_per_year"),
                      "merge_sigma_pp": m.get("sigma_diff_pp_per_year"),
                      "merge_cny_per_year": m.get("sigma_diff_cny_per_year")},
                     ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        face = _read_json(OUT_JSON)
        probs = check(face)
        if probs:
            print("CHECK_FAIL " + "; ".join(probs))
            return 1
        m = (face or {}).get("merge") or {}
        print("CHECK_OK rows=%d drift=%s merge_sigma=%s"
              % (len([r for r in (face or {}).get("rows") or [] if r.get("t_stat") is not None]),
                 ((face or {}).get("totals") or {}).get("drift_cny_per_year"),
                 m.get("sigma_diff_pp_per_year")))
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
