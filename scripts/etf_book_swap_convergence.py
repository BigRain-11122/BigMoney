"""ETF book -- the swap's harvest, measured on the pair's own prices.

r1522 priced the way out on the same close as the way in: four sides of cost on the executed
notional, with "prices unchanged" written down as a caveat. That number answers "what does
another exchange cost", not "does the gap ever come back far enough to be worth exchanging
back". The sheet has never answered the second question, and a reader cannot infer it from
either the mean gap or the percentile: a pair can sit wide for years and still never hand the
travelled pp back inside one rebalancing grid.

So this face measures the thing that was assumed. Same pair, same gap reconstruction as the
sibling-gap face (imported, not rebuilt), same executed notional as the way-out face:

  * two entry cohorts -- "tail" (sessions at least as wide as today) and "broad" (sessions at
    least as wide as the pair's own mean) -- because a cohort that only ever happened once
    cannot produce a distribution, and a distribution over everything is not today's question;
  * four horizons, 1/5/10/20 sessions, the last one being one rebalancing grid;
  * for each cohort x horizon: the median change of the gap (a narrowing gap is the swap
    holder's gain), the share of sessions that narrowed by more than the four-side toll, and
    the share that widened;
  * the median narrowing is then priced on the notional that actually traded and the toll is
    charged against it -- "net after paying both exchanges".

Censored sessions are counted, never scored as zero sessions (r1230 r0): a cohort member
whose forward window runs past the end of the panel is listed, not dropped silently.

Usage:
    python scripts/etf_book_swap_convergence.py run
    python scripts/etf_book_swap_convergence.py --check
    python scripts/etf_book_swap_convergence.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap_face  # noqa: E402  (the one gap reconstruction)

GAP_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")
STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
TRIGGER_FACE = os.path.join(ROOT, "results", "etf_book_swap_trigger.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_convergence.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_convergence.md")

HORIZONS = (1, 5, 10, 20)   # sessions; 20 = one REBAL grid
REFERENCE_H = 20            # the horizon the verdict is read on
MIN_COHORT = 8              # fewer than this is not a distribution
TAIL_EPS = 1e-9

CAVEATS = [
    "this measures the pair's relative price path after a wide session; it is not a book "
    "backtest -- nothing else in the book moves, no other name is re-ranked inside the horizon, "
    "and the decision to exchange back is assumed to be taken exactly at the horizon",
    "the cheap ticker is bought with the same money, so the harvest is a better entry into the "
    "same basket rather than a realised capital gain; the pp below is what the pair hands back, "
    "which is the number that decides whether a second exchange pays for its own four sides",
    "a cohort member whose forward window runs past the end of the panel is censored, not "
    "treated as a zero change (r1230 r0)",
    "the reconstruction inherits the sibling-gap face's single IOPV anchor; a premium base that "
    "shifted between the two tickers would move the level, not the change",
]


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def _refuse(face, why):
    face["verdict"] = "CANNOT_MEASURE"
    face["sentence"] = "这一问答不了：%s。" % why
    face["refused"] = why
    return face


def _cost_bp(trig):
    crit = (trig or {}).get("criteria") or {}
    v = crit.get("cost_bp_per_side")
    if v is None:
        return None
    return float(v)


def toll_pp(cost_bp):
    """Four sides: two to get in, two to get out."""
    return round(4.0 * float(cost_bp) / 100.0, 4)


def executed_notional(stack, leg):
    """The SELL row that moved this leg, and only if its reason says it was a swap."""
    for a in (stack or {}).get("actions") or []:
        if str(a.get("symbol")) != str(leg):
            continue
        if (a.get("side") or "").upper() != "SELL":
            continue
        if ("swap %s" % leg) not in (a.get("why") or ""):
            continue
        return a
    return None


def forward_deltas(rec, threshold, horizon):
    """Gap change `horizon` sessions after every session at or above `threshold`.

    Returns (deltas, censored, members). A member whose forward window is not inside the
    panel is counted as censored -- never as a zero change.
    """
    n = len(rec)
    deltas, censored, members = [], 0, 0
    for i in range(n):
        if rec[i] < threshold - TAIL_EPS:
            continue
        members += 1
        j = i + horizon
        if j >= n:
            censored += 1
            continue
        deltas.append(rec[j] - rec[i])
    return deltas, censored, members


def stats_for(deltas, censored, members, toll):
    """Distribution summary. An empty delta list is an absent reading, not a flat one."""
    out = {"members": members, "n": len(deltas), "censored": censored,
           "median_delta_pp": None, "mean_delta_pp": None,
           "share_narrowed_net_of_toll": None, "share_widened": None}
    if not deltas:
        return out
    out["median_delta_pp"] = round(statistics.median(deltas), 4)
    out["mean_delta_pp"] = round(statistics.fmean(deltas), 4)
    out["share_narrowed_net_of_toll"] = round(
        sum(1 for d in deltas if d <= -toll) / len(deltas), 4)
    out["share_widened"] = round(sum(1 for d in deltas if d > 0) / len(deltas), 4)
    return out


def measure_pair(pair, rec, notional, toll):
    """One pair: two cohorts x four horizons, then the reference verdict on horizon 20."""
    row = {"leg_symbol": pair.get("leg_symbol"), "sibling_symbol": pair.get("sibling_symbol"),
           "gap_today_pp": pair.get("gap_today_pp"),
           "mean_gap_pp": (pair.get("stats") or {}).get("mean_pp"),
           "notional_cny": None, "cohorts": {}, "verdict": None, "cohort_used": None,
           "net_after_toll_pp": None, "net_after_toll_cny": None, "why": ""}
    if notional is None:
        row["verdict"] = "NOT_SWAPPED_ON_THIS_BAR"
        row["why"] = "这张单没有换出这只票，问不到它的往返净额"
        return row
    row["notional_cny"] = round(float(notional), 2)
    today = row["gap_today_pp"]
    mean = row["mean_gap_pp"]
    if today is None or mean is None:
        row["verdict"] = "CANNOT_MEASURE"
        row["why"] = "价差面缺今日价差或均值"
        return row

    thresholds = {"tail": float(today), "broad": float(mean)}
    for name, thr in thresholds.items():
        block = {}
        for h in HORIZONS:
            deltas, censored, members = forward_deltas(rec, thr, h)
            block["h%d" % h] = stats_for(deltas, censored, members, toll)
        row["cohorts"][name] = block

    tail_ref = row["cohorts"]["tail"]["h%d" % REFERENCE_H]
    broad_ref = row["cohorts"]["broad"]["h%d" % REFERENCE_H]
    if tail_ref["n"] >= MIN_COHORT:
        used, ref = "tail", tail_ref
    elif broad_ref["n"] >= MIN_COHORT:
        used, ref = "broad", broad_ref
    else:
        row["verdict"] = "COHORT_TOO_SMALL"
        row["why"] = ("没有足够可比较的历史（尾部 %d 例、宽档 %d 例，门槛 %d）："
                      "少样本的「中位」不是分布" % (tail_ref["n"], broad_ref["n"], MIN_COHORT))
        return row
    row["cohort_used"] = used
    gain = -(ref["median_delta_pp"] or 0.0)
    net = round(gain - toll, 4)
    row["net_after_toll_pp"] = net
    row["net_after_toll_cny"] = round(float(notional) * net / 100.0, 2)
    row["verdict"] = "PAYS_MEASURED" if net > 0 else "DOES_NOT_PAY_MEASURED"
    return row


def compute(ctx):
    """Measure the harvest on the panels; refuse what cannot be measured.

    `ctx` carries the already-published faces: {"as_of", "sibling_gap", "swap_stack",
    "swap_trigger"}. The gap series itself is rebuilt with the sibling-gap module, so this
    face cannot disagree with the published gap about what the gap is.
    """
    as_of = ctx.get("as_of")
    face = {"artifact": "etf_book_swap_convergence", "bar": as_of, "evidence_cutoff": as_of,
            "verdict": None, "pairs": [], "totals": {}, "sentence": "", "refused": None,
            "horizons": list(HORIZONS), "reference_horizon": REFERENCE_H,
            "min_cohort": MIN_COHORT,
            "sources": {"sibling_gap": "results/etf_book_sibling_gap.json",
                        "swap_stack": "results/etf_book_swap_stack.json",
                        "swap_trigger": "results/etf_book_swap_trigger.json"},
            "caveats": list(CAVEATS)}

    gap = ctx.get("sibling_gap")
    stack = ctx.get("swap_stack")
    trig = ctx.get("swap_trigger")
    if not gap:
        return _refuse(face, "没有已发布的价差面（scripts/etf_book_sibling_gap.py run）")
    if not stack:
        return _refuse(face, "没有已发布的净额单面：不知道这张单动了多少钱")
    if not trig:
        return _refuse(face, "没有已发布的换票触发面：四边成本读不出来")
    cost = _cost_bp(trig)
    if cost is None:
        return _refuse(face, "触发面没有 cost_bp_per_side：成本缺省时净额就是编出来的数")
    toll = toll_pp(cost)
    face["cost_bp_per_side"] = cost
    face["toll_pp"] = toll

    stack_bar = stack.get("asof")
    if as_of and stack_bar and stack_bar != as_of:
        return _refuse(face, "净额单面停在 %s、这张单是 %s：两个 bar 的数不能相减（r1516 律）"
                       % (stack_bar, as_of))

    rows, skipped = [], []
    for pair in gap.get("pairs") or []:
        leg = str(pair.get("leg_symbol"))
        act = executed_notional(stack, leg)
        if act is None:
            skipped.append({"leg_symbol": leg,
                            "sibling_symbol": pair.get("sibling_symbol"),
                            "why": "这张单没有换出这只票"})
            continue
        files = pair.get("daily_files") or []
        if len(files) != 2 or not all(files):
            rows.append({"leg_symbol": leg, "verdict": "CANNOT_MEASURE",
                         "why": "这一对没有本地日线面板"})
            continue
        try:
            a = gap_face.load_close(os.path.join(ROOT, files[0]))
            b = gap_face.load_close(os.path.join(ROOT, files[1]))
        except OSError as exc:
            rows.append({"leg_symbol": leg, "verdict": "CANNOT_MEASURE",
                         "why": "面板读不出：%r" % (exc,)})
            continue
        dates, ca, cb = gap_face.common_series(a, b)
        if len(dates) < gap_face.MIN_DAYS:
            rows.append({"leg_symbol": leg, "verdict": "CANNOT_MEASURE",
                         "why": "共同交易日只有 %d 根（门槛 %d）"
                                % (len(dates), gap_face.MIN_DAYS)})
            continue
        g = gap_face.gap_series(ca, cb)
        rec, _offset = gap_face.reconstruct(g, pair.get("gap_today_pp"))
        if not rec:
            rows.append({"leg_symbol": leg, "verdict": "CANNOT_MEASURE",
                         "why": "价差重建是空的"})
            continue
        row = measure_pair(pair, rec, act.get("amount_cny"), toll)
        row["sessions"] = len(rec)
        rows.append(row)

    face["pairs"] = rows
    if skipped:
        face["skipped"] = skipped
    priced = [r for r in rows if r.get("verdict") in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED")]
    if not priced:
        face["verdict"] = "NOTHING_MEASURED"
        face["sentence"] = ("这一单没有可测量的换票：换出的票没有历史价差路径，"
                            "或者可比较的样本太少——这不是「不赚钱」的结论。")
        return face

    face["totals"] = {
        "measured_pairs": len(priced),
        "pays_pairs": sum(1 for r in priced if r["verdict"] == "PAYS_MEASURED"),
        "notional_cny": round(sum(r.get("notional_cny") or 0.0 for r in priced), 2),
        "net_after_toll_cny": round(sum(r.get("net_after_toll_cny") or 0.0 for r in priced), 2),
    }
    face["verdict"] = ("PAYS_MEASURED" if face["totals"]["net_after_toll_cny"] > 0
                       else "DOES_NOT_PAY_MEASURED")
    face["sentence"] = sentence(face)
    return face


def _fmt(x):
    return format(float(x or 0.0), ",.0f")


def _pp(v, nd=2):
    return "读不出" if v is None else ("%+.*f" % (nd, v))


def _pct(v):
    return "读不出" if v is None else "%.0f%%" % (100.0 * v)


def _money_signed(v):
    """A loss reads as a loss: -¥369, not ¥-369 (a reader misses the sign inside the mark)."""
    if v is None:
        return "读不出"
    v = float(v)
    return ("-%s%s" % ("\u00a5", _fmt(abs(v)))) if v < 0 else ("%s%s" % ("\u00a5", _fmt(v)))


def sentence(face):
    t = face.get("totals") or {}
    rows = [r for r in face.get("pairs") or []
            if r.get("verdict") in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED")]
    if not rows:
        return face.get("sentence") or ""
    parts = []
    for r in rows:
        ref = ((r.get("cohorts") or {}).get(r.get("cohort_used")) or {}).get(
            "h%d" % REFERENCE_H) or {}
        parts.append("%s（%s 档 %d 例）%d 个交易日后价差中位变化 %s pp，扣掉四边 %s pp 后净 %s pp"
                     % (r["leg_symbol"], "今日同宽" if r.get("cohort_used") == "tail" else "宽于均值",
                        ref.get("n") or 0, REFERENCE_H,
                        _pp(ref.get("median_delta_pp")), "%.2f" % (face.get("toll_pp") or 0.0),
                        _pp(r.get("net_after_toll_pp"), 4)))
    return ("换回来的收益是量出来的、不是假设价不变：%s。"
            "按实际换出的 %s 算，合计净 %s。"
            % ("；".join(parts), _money_signed(t.get("notional_cny")),
               _money_signed(t.get("net_after_toll_cny"))))


def md_lines(face, heading="## 换回来的收益量出来是多少（r1523）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的收敛面（跑 "
                "scripts/etf_book_swap_convergence.py run）。缺面不等于换回来不赚钱。", ""]
    if face.get("refused"):
        return ["", heading, "- **算不出来**：%s。" % face["refused"],
                "- 读法：这一节只对已发布的价差序列做测量，不猜价差也不猜成本；"
                "「算不出来」与「不赚钱」是两件事。", ""]
    L = ["", heading, "- %s" % (face.get("sentence") or "")]
    rows = face.get("pairs") or []
    if rows:
        L += ["", "| 换出 | 换入 | 样本档 | 例数 | 1 日后 | 5 日后 | 10 日后 | 20 日后 | 越过四边成本的比例 | 净 pp | 净金额 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            coh = (r.get("cohorts") or {}).get(r.get("cohort_used")) or {}
            cells = []
            for h in HORIZONS:
                cells.append(_pp(((coh.get("h%d" % h) or {}).get("median_delta_pp"))))
            ref = coh.get("h%d" % REFERENCE_H) or {}
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (r.get("leg_symbol"), r.get("sibling_symbol"),
                        {"tail": "今日同宽", "broad": "宽于均值"}.get(r.get("cohort_used"), "无"),
                        ref.get("n") if ref.get("n") is not None else 0,
                        cells[0], cells[1], cells[2], cells[3],
                        _pct(ref.get("share_narrowed_net_of_toll")),
                        _pp(r.get("net_after_toll_pp"), 4),
                        _money_signed(r.get("net_after_toll_cny")) if r.get("notional_cny") else "—"))
        L += ["", "- 表里的数是**价差的变化**：负数＝价差收窄＝换回来的人赚到。"
                  "「净 pp」= 20 日中位收窄 - 四边成本（%.2f pp），"
                  "再按这张单实际换出的 %s 折成钱。"
              % (face.get("toll_pp") or 0.0, _money_signed((face.get("totals") or {}).get("notional_cny"))),
              "- 与「换进去赚了多少」不是同一个数：换进便宜的那只，赚的是**同一笔钱买到更多份额**（水平效应，"
              "换过去当天就成立）；这一节量的是**价差后来有没有回来**（路径效应），"
              "它只决定「换回来」这一笔值不值。两个数不能相加，也不能互相印证。"]
        tails = [(r["leg_symbol"], (r.get("cohorts") or {}).get("tail") or {})
                 for r in rows]
        if tails:
            refs = [((c.get("h%d" % REFERENCE_H)) or {}) for _, c in tails]
            if all((x.get("n") or 0) < MIN_COHORT for x in refs):
                L.append("- **今天的宽度没有可比历史**：今日同宽档 20 日后只有 %s 例（门槛 %d），"
                         "所以判决退到「宽于均值」档——那一档里今天的极端宽度并不常见，"
                         "读到的是**同一个价差方向上的常态**，不是今天这一根 bar 的独占命运。"
                         % ("/".join(str(x.get("n") or 0) for x in refs), MIN_COHORT))
        cens = [(r["leg_symbol"], (r.get("cohorts") or {}).get(r.get("cohort_used")) or {})
                for r in rows if r.get("cohort_used")]
        tail_cens = [((c.get("h%d" % REFERENCE_H) or {}).get("censored") or 0) for _, c in cens]
        if any(tail_cens):
            L.append("- 未愈合样本（前向窗口超出面板）%s 例，单独计数、没当成 0 变化。"
                     % "/".join(str(x) for x in tail_cens))
        small = [r["leg_symbol"] for r in rows if r.get("verdict") == "COHORT_TOO_SMALL"]
        if small:
            L.append("- 样本太少、不出判决的：%s（%s）。"
                     % ("、".join(small), "；".join(r.get("why") or "" for r in rows
                                                    if r.get("verdict") == "COHORT_TOO_SMALL")))
        nv = [r["leg_symbol"] for r in rows if r.get("verdict") == "NOT_SWAPPED_ON_THIS_BAR"]
        if nv:
            L.append("- 这一单没有换出、所以没有往返的：%s。" % "、".join(nv))
    elif face.get("verdict") == "NOTHING_MEASURED":
        L.append("- 这一单没有可测量的换票；这不是「不赚钱」的结论。")
    if face.get("skipped"):
        L.append("- 未计入的票：%s。"
                 % "；".join("%s（%s）" % (s.get("leg_symbol"), s.get("why"))
                            for s in face["skipped"]))
    return L


def check(face):
    """Re-derive the arithmetic the payload claims. Absent readings are not failures."""
    problems = []
    if not face:
        return ["no face"]
    if face.get("verdict") in ("CANNOT_MEASURE", "NOTHING_MEASURED"):
        return problems
    toll = face.get("toll_pp")
    want_toll = round(4.0 * float(face.get("cost_bp_per_side") or 0.0) / 100.0, 4)
    if toll is None or abs(want_toll - toll) > 1e-9:
        problems.append("toll_pp %s != 4 sides of %s" % (toll, face.get("cost_bp_per_side")))
    for r in face.get("pairs") or []:
        if r.get("verdict") not in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED"):
            continue
        coh = (r.get("cohorts") or {}).get(r.get("cohort_used")) or {}
        ref = coh.get("h%d" % REFERENCE_H) or {}
        med = ref.get("median_delta_pp")
        if med is None:
            problems.append("%s has no %d-session median" % (r["leg_symbol"], REFERENCE_H))
            continue
        want_net = round(-med - toll, 4)
        if abs(want_net - (r.get("net_after_toll_pp") or 0.0)) > 1e-6:
            problems.append("%s net %s != %s" % (r["leg_symbol"], r.get("net_after_toll_pp"),
                                                 want_net))
        if r.get("notional_cny"):
            want_cny = round(float(r["notional_cny"]) * (r.get("net_after_toll_pp") or 0.0)
                             / 100.0, 2)
            if abs(want_cny - (r.get("net_after_toll_cny") or 0.0)) > 0.011:
                problems.append("%s cny %s != %s" % (r["leg_symbol"],
                                                     r.get("net_after_toll_cny"), want_cny))
        if r.get("verdict") == "PAYS_MEASURED" and (r.get("net_after_toll_pp") or 0.0) <= 0:
            problems.append("%s says PAYS with a non-positive net" % r["leg_symbol"])
        if r.get("verdict") == "DOES_NOT_PAY_MEASURED" and (r.get("net_after_toll_pp") or 0.0) > 0:
            problems.append("%s says DOES_NOT_PAY with a positive net" % r["leg_symbol"])
        for name, block in (r.get("cohorts") or {}).items():
            for h, st in block.items():
                if st.get("members") != (st.get("n") or 0) + (st.get("censored") or 0):
                    problems.append("%s %s %s: members != n + censored"
                                    % (r["leg_symbol"], name, h))
    t = face.get("totals") or {}
    if t:
        paid = [r for r in face.get("pairs") or []
                if r.get("verdict") in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED")]
        if abs(round(sum(r.get("net_after_toll_cny") or 0.0 for r in paid), 2)
               - (t.get("net_after_toll_cny") or 0.0)) > 0.011:
            problems.append("totals do not add up")
        if (t.get("pays_pairs") or 0) > (t.get("measured_pairs") or 0):
            problems.append("more pairs pay than were measured")
    return problems


# ---------------------------------------------------------------- selftest fixtures

def _fixture():
    """A 120-session pair: calm, one wide episode, then it narrows back to calm."""
    rec = []
    for i in range(120):
        if i < 40:
            rec.append(0.5)
        elif i < 45:
            rec.append(6.0 - 0.1 * (i - 40))          # 6.0 .. 5.6
        elif i < 60:
            rec.append(5.6 - 0.34 * (i - 45))         # 5.6 .. 0.5
        else:
            rec.append(0.5)
    gap = {"artifact": "etf_book_sibling_gap", "session": "2026-11-10",
           "pairs": [{"leg_symbol": "159501", "sibling_symbol": "159513",
                      "gap_today_pp": 3.5,
                      "daily_files": ["data/daily/sz159501.csv",
                                      "data/daily/sz159513.csv"],
                      "stats": {"mean_pp": 2.0}}]}
    stack = {"asof": "2026-11-10",
             "actions": [{"side": "SELL", "symbol": "159501", "lots": 372, "price": 2.11,
                          "amount_cny": 78492.0, "why": "swap 159501 -> 159513"},
                         {"side": "BUY", "symbol": "159513", "lots": 891, "price": 1.76,
                          "amount_cny": 156816.0, "why": "merged buy"}]}
    trig = {"criteria": {"cost_bp_per_side": 8.0, "toll_pp": 0.16}}
    return {"as_of": "2026-11-10", "sibling_gap": gap, "swap_stack": stack,
            "swap_trigger": trig}, rec


def _fake_load(rec):
    """Patch the panel readers so the fixture series is the panel."""
    n = len(rec)
    dates = ["d%03d" % i for i in range(n)]
    closes_a = [100.0 * (1.0 + 0.0001 * i) for i in range(n)]
    closes_b = list(closes_a)

    def load_close(_path):
        return {d: v for d, v in zip(dates, closes_a)}

    def common_series(a, b):
        return dates, [a[d] for d in dates], [b[d] for d in dates]

    return load_close, common_series


def _compute_with_rec(rec, ctx=None):
    ctx = ctx or _fixture()[0]
    orig = (gap_face.load_close, gap_face.common_series, gap_face.gap_series,
            gap_face.reconstruct, gap_face.MIN_DAYS)
    load, common = _fake_load(rec)
    gap_face.load_close = load
    gap_face.common_series = lambda a, b: (sorted(a), [a[d] for d in sorted(a)],
                                           [b[d] for d in sorted(a)])
    gap_face.gap_series = lambda ca, cb: list(rec)
    gap_face.reconstruct = lambda g, gap_today: (list(rec), 0.0)
    gap_face.MIN_DAYS = 10
    try:
        return compute(ctx)
    finally:
        (gap_face.load_close, gap_face.common_series, gap_face.gap_series,
         gap_face.reconstruct, gap_face.MIN_DAYS) = orig


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    leg("L1 four sides of 8bp is 0.32pp", abs(toll_pp(8.0) - 0.32) < 1e-9)
    leg("L2 toll scales with the cost input", abs(toll_pp(20.0) - 0.80) < 1e-9)

    rec = [1.0, 2.0, 5.0, 4.0, 3.0]
    d, cens, members = forward_deltas(rec, 4.0, 2)
    leg("L3 only sessions at or above the threshold enter the cohort",
        members == 2 and d == [-2.0], (d, cens, members))
    leg("L4 a member whose window runs past the panel is censored, not zero",
        cens == 1, (d, cens))
    d0, cens0, _m0 = forward_deltas(rec, 99.0, 1)
    leg("L5 an empty cohort reads as empty, not as a flat distribution",
        d0 == [] and stats_for(d0, 0, 0, 0.32)["median_delta_pp"] is None)

    st = stats_for([-2.0, -1.0, 0.5, 0.1], 2, 6, 0.32)
    leg("L6 median change is the middle of the deltas", st["median_delta_pp"] == -0.45, st)
    leg("L7 net-of-toll share counts only narrowing past the toll",
        st["share_narrowed_net_of_toll"] == 0.5, st)
    leg("L8 widened share counts strictly positive changes", st["share_widened"] == 0.5, st)

    # an executed pair whose gap narrows after a wide session pays
    ctx, bare = _fixture()
    f = _compute_with_rec(bare)
    leg("L9 a narrowing pair is measured as paying", f["verdict"] == "PAYS_MEASURED", f["verdict"])
    row = f["pairs"][0]
    leg("L10 the executed notional comes from the SELL row",
        abs(row["notional_cny"] - 78492.0) < 0.011, row["notional_cny"])
    leg("L11 net is the narrowing minus four sides",
        abs(row["net_after_toll_pp"] - (-(row["cohorts"][row["cohort_used"]]["h20"]
                                          ["median_delta_pp"]) - 0.32)) < 1e-6)
    leg("L12 check() is clean on the clean face", check(f) == [], check(f))
    leg("L13 md carries the measured number", any("净" in x for x in md_lines(f)))

    # a widening pair does not pay
    wide = [2.0] * 120
    for i in range(40, 120):
        wide[i] = 2.0 + 0.3 * (i - 40)
    f2 = _compute_with_rec(wide)
    leg("L14 a widening pair is measured as not paying",
        f2["verdict"] == "DOES_NOT_PAY_MEASURED", f2["verdict"])
    leg("L15 a non-paying face still prices its rows", check(f2) == [], check(f2))

    # censoring survives to the face
    short = [6.0] * 12
    f3 = _compute_with_rec(short)
    row3 = (f3.get("pairs") or [{}])[0]
    leg("L16 a mostly-censored panel cannot produce a median",
        row3.get("verdict") in ("COHORT_TOO_SMALL", "NOTHING_MEASURED")
        or row3.get("cohort_used") is None, row3.get("verdict"))

    # refusals
    c4 = _fixture()[0]
    c4["swap_trigger"] = None
    leg("L17 missing trigger refuses", _compute_with_rec(bare, c4)["verdict"] == "CANNOT_MEASURE")
    c5 = _fixture()[0]
    del c5["swap_trigger"]["criteria"]["cost_bp_per_side"]
    leg("L18 missing cost refuses", _compute_with_rec(bare, c5)["verdict"] == "CANNOT_MEASURE")
    c6 = _fixture()[0]
    c6["swap_stack"]["asof"] = "2026-11-11"
    leg("L19 a stack from another bar is refused",
        _compute_with_rec(bare, c6)["verdict"] == "CANNOT_MEASURE")

    # an unexecuted pair is named, not measured
    c7 = _fixture()[0]
    c7["swap_stack"]["actions"] = [c7["swap_stack"]["actions"][1]]
    f7 = _compute_with_rec(bare, c7)
    leg("L20 a pair this bar did not swap is named as such",
        f7["verdict"] == "NOTHING_MEASURED"
        and any(s.get("leg_symbol") == "159501" for s in (f7.get("skipped") or [])), f7["verdict"])

    # a trim is not a swap
    c8 = _fixture()[0]
    c8["swap_stack"]["actions"][0]["why"] = "floor trim 159501 to 372 lots"
    leg("L21 a SELL without a swap reason is not priced",
        _compute_with_rec(bare, c8)["verdict"] == "NOTHING_MEASURED")

    # tampering is caught
    f9 = json.loads(json.dumps(f))
    f9["pairs"][0]["net_after_toll_pp"] += 0.5
    leg("L22 check catches a tampered net", check(f9) != [])
    f10 = json.loads(json.dumps(f))
    f10["toll_pp"] = 0.16
    leg("L23 check catches a two-side toll where four sides were charged", check(f10) != [])
    f11 = json.loads(json.dumps(f))
    f11["pairs"][0]["cohorts"]["tail"]["h1"]["members"] = 99
    leg("L24 check catches censored sessions that went missing", check(f11) != [])

    # md: absent face and refused face both print a line
    leg("L25 absent face prints a refusal line", any("跑 scripts" in x for x in md_lines(None)))
    c9 = _fixture()[0]
    c9["sibling_gap"] = None
    leg("L26 a missing gap face prints its reason",
        any("算不出来" in x for x in md_lines(_compute_with_rec(bare, c9))))

    ok = sum(1 for _, v, _d in legs if v)
    print("etf_book_swap_convergence selftest %d/%d" % (ok, len(legs)))
    for n, v, d in legs:
        print("  %-6s %s%s" % ("PASS" if v else "FAIL", n,
                               "" if v else "  :: %r" % (d,)))
    return 0 if ok == len(legs) else 1


def _emit(line):
    """Console-safe print: a GBK terminal must not be able to kill a published face."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "backslashreplace").decode("ascii"))


def run():
    gap = _read_json(GAP_JSON)
    stack = _read_json(STACK_FACE)
    trig = _read_json(TRIGGER_FACE)
    as_of = (stack or {}).get("asof") or (gap or {}).get("session")
    face = compute({"as_of": as_of, "sibling_gap": gap, "swap_stack": stack,
                    "swap_trigger": trig})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    L = ["# 换回来的收益量出来是多少（r1523）", "",
         "bar %s ｜ 判定 **%s**" % (as_of, face["verdict"]), ""]
    L += md_lines(face, heading="## 逐对读数")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    _emit(json.dumps({"verdict": face["verdict"],
                      "pairs": len(face.get("pairs") or []),
                      "net_after_toll_cny": (face.get("totals") or {}).get("net_after_toll_cny"),
                      "sentence": face.get("sentence")}, ensure_ascii=False))
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
        rows = len([r for r in (face or {}).get("pairs") or []
                    if r.get("verdict") in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED")])
        print("CHECK_OK measured=%d" % rows)
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
