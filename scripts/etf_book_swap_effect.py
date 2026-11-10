"""ETF book -- the swap's gain and the swap's path are two readings of ONE gap.

r1467 put a CNY gain on the sheet next to the swap (`swap_repricing`: the same money buys
more basket units because the sibling is cheaper). r1523 measured, on the pair's own prices,
whether that gap ever comes back inside one rebalancing grid. Both numbers are on the sheet,
in two different sections, and nothing says how they relate:

  * 159501 -> 159513  "进价差赚 ¥5,612.5"
  * 159501 -> 159513  "20 日后价差中位 +0.15pp, 扣四边净 -0.4705pp = -¥369"

Read side by side, a reader can only conclude one of two things, and both are wrong: that the
book earned 5,612 and then lost 369 (a net of 5,243), or that the -369 contradicts the 5,612
and one of them must be wrong. Neither is what happened.

The two are the same gap read twice:

  * LEVEL  -- how wide the discount is today, converted into money (extra units bought with
              the same cash). It is a size, not a harvest, and it becomes cash only when the
              gap narrows.
  * PATH   -- whether that narrowing happened, on the pair's own forward history, net of the
              four sides a round trip pays. It is the realisation condition of the level.

Adding them counts the discount twice. Subtracting them compares a size with a frequency.
This face prints them on one line, states which one is the condition of the other, and
refuses to produce a combined number at all -- the field exists and is `None` on purpose, so
a downstream tool cannot quietly sum what a human was told not to.

Usage:
    python scripts/etf_book_swap_effect.py run
    python scripts/etf_book_swap_effect.py --check
    python scripts/etf_book_swap_effect.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_swap_convergence as conv_face  # noqa: E402  (one implementation of "which SELL was a swap")

STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
CONV_FACE = os.path.join(ROOT, "results", "etf_book_swap_convergence.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_effect.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_effect.md")

CENT = 0.011          # one cent: two faces that price the same trade agree to the cent

WHY_NOT_ADDED = (
    "水平效应是「折扣有多宽」，路径效应是「折扣有没有被收回」——同一根价差的两种读法；"
    "相加＝把折扣算两遍，相减＝拿大小比频率。本面故意不提供合计值。")


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _refuse(face, why):
    face["verdict"] = "CANNOT_PAIR"
    face["refused"] = why
    face["sentence"] = "这一问答不了：%s。" % why
    return face


def level_rows(stack):
    """{leg: gain on the trimmed book} -- the stack's own CNY figure, not re-derived here."""
    out = {}
    for r in (stack or {}).get("swap_repricing") or []:
        leg = r.get("leg")
        gain = r.get("gain_on_trimmed_book_cny")
        if leg is None or gain is None:
            continue
        out[str(leg)] = {"gain_cny": float(gain),
                         "share": r.get("share"),
                         "published_cny": r.get("gain_published_cny")}
    return out


def path_rows(convergence):
    """{leg: the measured way-out row} for pairs the convergence face could actually judge."""
    out = {}
    for r in (convergence or {}).get("pairs") or []:
        leg = r.get("leg_symbol")
        if leg is None:
            continue
        out[str(leg)] = r
    return out


def _ref_of(row):
    coh = ((row or {}).get("cohorts") or {}).get(row.get("cohort_used")) or {}
    return coh.get("h%d" % conv_face.REFERENCE_H) or {}


def pair_one(leg, level, path, notional):
    """One leg: the discount, the measured path, and the distance between them.

    A row is only priced when BOTH face it and both priced the SAME trade. Anything less is
    named with its reason -- never printed as a zero (r1261 family: an empty reading is not
    a good reading).
    """
    row = {"leg_symbol": leg, "sibling_symbol": (path or {}).get("sibling_symbol"),
           "notional_cny": notional, "level_cny": None, "narrowing_needed_pp": None,
           "path_pp": None, "path_cny": None, "median_delta_pp": None,
           "cohort_used": None, "cohort_n": None, "share_crossing_toll": None,
           "same_trade": False, "why": ""}

    if level is None:
        row["why"] = "换票触发面/净额单没有给这一对定价（水平效应读不出来）"
        return row
    if path is None:
        row["why"] = "换出了，但收敛面没有这一对（路径没量过）"
        return row
    if path.get("verdict") not in ("PAYS_MEASURED", "DOES_NOT_PAY_MEASURED"):
        row["why"] = "路径量测没出结论：%s" % (path.get("why") or path.get("verdict"))
        return row

    p_notional = path.get("notional_cny")
    if notional is not None and p_notional is not None and abs(float(notional)
                                                               - float(p_notional)) > CENT:
        row["why"] = ("两个面量的是不同的一笔：净额单换出 ¥%s，收敛面按 ¥%s 算"
                      % (format(float(notional), ",.2f"), format(float(p_notional), ",.2f")))
        return row

    row["same_trade"] = True
    row["level_cny"] = round(float(level["gain_cny"]), 2)
    base = float(notional if notional is not None else (p_notional or 0.0))
    if base > 0:
        # the discount expressed as the narrowing it needs, so a reader can compare it with
        # the path column with eyes open -- it is NOT the level minus the path.
        row["narrowing_needed_pp"] = round(100.0 * row["level_cny"] / base, 2)
    ref = _ref_of(path)
    row["path_pp"] = path.get("net_after_toll_pp")
    row["path_cny"] = path.get("net_after_toll_cny")
    row["median_delta_pp"] = ref.get("median_delta_pp")
    row["cohort_used"] = path.get("cohort_used")
    row["cohort_n"] = ref.get("n")
    row["share_crossing_toll"] = ref.get("share_narrowed_net_of_toll")
    return row


def compute(ctx):
    """Pair the stack's CNY gain with the convergence face's measured path.

    `ctx` carries the already-published faces: {"as_of", "swap_stack", "swap_convergence"}.
    Nothing is recomputed from panels here -- a second derivation of the gap would be a second
    place for it to drift (r1375).
    """
    as_of = ctx.get("as_of")
    face = {"artifact": "etf_book_swap_effect", "bar": as_of, "evidence_cutoff": as_of,
            "verdict": None, "rows": [], "unpaired": [], "totals": {}, "sentence": "",
            "sum_refused": WHY_NOT_ADDED, "refused": None,
            "reference_horizon": conv_face.REFERENCE_H,
            "sources": {"swap_stack": "results/etf_book_swap_stack.json",
                        "swap_convergence": "results/etf_book_swap_convergence.json"},
            "caveats": [
                "the level figure is the stack's own number (already re-scaled on the trimmed "
                "book); it is not re-derived from the panels here, so a stack that priced the "
                "wrong size would carry through",
                '"narrowing_needed_pp" is the discount divided by the traded amount -- a size, '
                "not a forecast, and it must not be subtracted from the path column",
                "the path column is a median over a cohort, not this session's own future: it "
                "says what comparable sessions did, and the cohort it was read on is named",
                "neither column prices tracking difference, fee, size or FX-hedge policy "
                "between the two tickers",
            ]}

    stack = ctx.get("swap_stack")
    conv = ctx.get("swap_convergence")
    if not stack:
        return _refuse(face, "没有已发布的净额单面（scripts/etf_book_swap_stack.py run）")
    if not conv:
        return _refuse(face, "没有已发布的收敛面（scripts/etf_book_swap_convergence.py run）")
    s_bar = stack.get("asof") or stack.get("bar")
    c_bar = conv.get("bar")
    if as_of and ((s_bar and s_bar != as_of) or (c_bar and c_bar != as_of)):
        return _refuse(face, "净额单面停在 %s、收敛面停在 %s、这张单是 %s：不同 bar 的数不能并列"
                       % (s_bar, c_bar, as_of))

    levels = level_rows(stack)
    paths = path_rows(conv)
    rows, unpaired = [], []
    for leg in sorted(set(levels) | set(paths)):
        notional = None
        act = conv_face.executed_notional(stack, leg)
        if act is not None:
            notional = float(act.get("amount_cny") or 0.0)
        row = pair_one(leg, levels.get(leg), paths.get(leg), notional)
        if row["same_trade"]:
            rows.append(row)
        else:
            unpaired.append({"leg_symbol": leg,
                             "sibling_symbol": row.get("sibling_symbol"),
                             "level_cny": row.get("level_cny"),
                             "path_pp": row.get("path_pp"),
                             "why": row["why"]})

    face["rows"] = rows
    face["unpaired"] = unpaired
    if not rows:
        face["verdict"] = "CANNOT_PAIR"
        face["sentence"] = ("这一单没有可以并列的换票：%s——这不是「不赚钱」的结论。"
                            % ("；".join(u["why"] for u in unpaired) or "两张面没有共同的票"))
        face["totals"] = {"level_cny": None, "path_cny": None, "combined_cny": None,
                          "priced_legs": 0, "why_not_added": WHY_NOT_ADDED}
        return face

    face["totals"] = {
        "level_cny": round(sum(r["level_cny"] for r in rows), 2),
        "path_cny": round(sum(float(r["path_cny"] or 0.0) for r in rows), 2),
        # deliberately absent: see WHY_NOT_ADDED. The key exists so a reader can see the
        # refusal instead of wondering whether the sum was forgotten.
        "combined_cny": None,
        "priced_legs": len(rows),
        "why_not_added": WHY_NOT_ADDED,
    }
    pays = [r for r in rows if float(r["path_cny"] or 0.0) > 0]
    face["verdict"] = ("DISCOUNT_PARTLY_COLLECTED" if pays else "DISCOUNT_UNCOLLECTED")
    face["sentence"] = sentence(face)
    return face


def _money(v):
    if v is None:
        return "读不出"
    v = float(v)
    return ("-%s%s" % ("\u00a5", format(abs(v), ",.0f"))) if v < 0 \
        else ("%s%s" % ("\u00a5", format(v, ",.0f")))


def _pp(v):
    return "读不出" if v is None else "%+.2fpp" % float(v)


def _pct(v):
    return "读不出" if v is None else "%.0f%%" % (100.0 * float(v))


def sentence(face):
    rows = face.get("rows") or []
    t = face.get("totals") or {}
    if not rows:
        return face.get("sentence") or ""
    bits = []
    for r in rows:
        bits.append("%s 折扣 %s（要兑现得收窄 %s pp），20 个交易日后价差中位 %s、扣四边净 %s（%s）"
                    % (r["leg_symbol"], _money(r["level_cny"]),
                       "读不出" if r["narrowing_needed_pp"] is None
                       else "%.2f" % r["narrowing_needed_pp"],
                       _pp(r["median_delta_pp"]), _pp(r["path_pp"]),
                       _money(r["path_cny"])))
    head = ("这两个数不能相加：进价差赚的 %s 是「同一笔钱在今天这根 bar 上多买到的份额」，"
            "而 %d 个交易日后的价差是量出来的——前者量折扣有多宽，后者量折扣有没有被收回，"
            "同一根价差的两种读法，加起来就是把折扣算两遍。"
            % (_money(t.get("level_cny")), conv_face.REFERENCE_H))
    cross = [r for r in rows if r.get("share_crossing_toll") is not None]
    tail = ""
    if cross:
        tail = ("可比历史里真正越过四边成本的比例：%s；合计路径 %s（不是加在折扣上，是折扣的兑现率）。"
                % ("、".join("%s %s" % (r["leg_symbol"], _pct(r["share_crossing_toll"]))
                             for r in cross), _money(t.get("path_cny"))))
    return head + "；".join(bits) + "。" + tail


def md_lines(face, heading="## 换进去赚的和换回来量的：一行两个数，不能相加（r1524）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的并列面（跑 "
                "scripts/etf_book_swap_effect.py run）。缺面不等于这两个数可以相加。", ""]
    if face.get("refused"):
        return ["", heading, "- **算不出来**：%s。" % face["refused"],
                "- 读法：这一节只并列两张已发布的面，不重算价差也不重算收益；"
                "「算不出来」与「换票不赚钱」是两件事。", ""]
    L = ["", heading, "- %s" % (face.get("sentence") or "")]
    rows = face.get("rows") or []
    if rows:
        L += ["", "| 换出 | 换入 | 成交额 | 进价差赚（水平·今天成立） | 要兑现得收窄 | "
                  "20 日后价差中位 | 扣四边净 | 净金额 | 越过四边成本的比例 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| %s | %s | %s | **%s** | %s | %s | %s | %s | %s |"
                     % (r["leg_symbol"], r.get("sibling_symbol") or "?",
                        _money(r.get("notional_cny")), _money(r["level_cny"]),
                        "读不出" if r["narrowing_needed_pp"] is None
                        else "%.2f pp" % r["narrowing_needed_pp"],
                        _pp(r["median_delta_pp"]), _pp(r["path_pp"]),
                        _money(r["path_cny"]), _pct(r.get("share_crossing_toll"))))
        L += ["",
              "- **这两个数不能相加**：%s" % (face.get("sum_refused") or WHY_NOT_ADDED),
              "- 读法：水平那一列是**折扣的大小**（同一笔钱多买到多少份额，今天成立、"
              "卖出时才结算）；路径那几列是**折扣有没有被收回**（这对票自己的前向历史，"
              "扣掉往返四边）。折扣要变成现金，价差得净收窄到上面写的那个数——"
              "而可比历史里发生过的中位变化写在它右边。"]
        _small = [(r["leg_symbol"], r.get("cohort_n") or 0) for r in rows
                  if (r.get("cohort_n") or 0) < conv_face.MIN_COHORT]
        if _small:
            L.append("- **判决不是读在「今日同宽」档上**：%s 的样本只有 %s 例（门槛 %d），"
                     "所以路径读的是「宽于均值」档——同一个价差方向上的常态，"
                     "不是今天这根 bar 的独占命运。"
                     % ("、".join(s for s, _n in _small),
                        "/".join(str(n) for _s, n in _small), conv_face.MIN_COHORT))
    else:
        L.append("- 这一单没有可以并列的换票；这不是「不赚钱」的结论。")
    if face.get("unpaired"):
        L.append("- 没并列的票：%s。"
                 % "；".join("%s（%s）" % (u.get("leg_symbol"), u.get("why"))
                            for u in face["unpaired"]))
    return L


def check(face):
    """Re-derive what the payload claims. A refusal is not a failure; a combined total is."""
    problems = []
    if not face:
        return ["no face"]
    t = face.get("totals") or {}
    if t.get("combined_cny") is not None:
        problems.append("totals carries a combined number, which the face refuses to make")
    for key in t:
        if key in ("level_cny", "path_cny", "combined_cny", "priced_legs", "why_not_added"):
            continue
        problems.append("unexpected totals key %r" % (key,))
    if face.get("verdict") == "CANNOT_PAIR":
        return problems
    rows = face.get("rows") or []
    if not rows:
        problems.append("a verdict without rows")
        return problems
    for r in rows:
        if not r.get("same_trade"):
            problems.append("%s is priced but the two faces did not price the same trade"
                            % r.get("leg_symbol"))
        notional = float(r.get("notional_cny") or 0.0)
        level = r.get("level_cny")
        if notional <= 0 or level is None:
            problems.append("%s has no usable notional or level" % r.get("leg_symbol"))
            continue
        want = round(100.0 * float(level) / notional, 2)
        if r.get("narrowing_needed_pp") is None or abs(want - float(r["narrowing_needed_pp"])) > 0.011:
            problems.append("%s narrowing %s != level/notional %s"
                            % (r["leg_symbol"], r.get("narrowing_needed_pp"), want))
    if abs(round(sum(float(r.get("level_cny") or 0.0) for r in rows), 2)
           - float(t.get("level_cny") or 0.0)) > 1e-6:
        problems.append("level totals do not add up")
    if abs(round(sum(float(r.get("path_cny") or 0.0) for r in rows), 2)
           - float(t.get("path_cny") or 0.0)) > 1e-6:
        problems.append("path totals do not add up")
    pays = [r for r in rows if float(r.get("path_cny") or 0.0) > 0]
    want_v = "DISCOUNT_PARTLY_COLLECTED" if pays else "DISCOUNT_UNCOLLECTED"
    if face.get("verdict") != want_v:
        problems.append("%s does not follow from the rows (%s)" % (face.get("verdict"), want_v))
    if not any("这两个数不能相加" in x for x in md_lines(face)):
        problems.append("the page never says the two columns cannot be added")
    return problems


# ---------------------------------------------------------------- selftest fixtures

def _fixture():
    stack = {"asof": "2026-11-10",
             "actions": [
                 {"side": "SELL", "symbol": "159501", "lots": 372, "price": 2.11,
                  "amount_cny": 78492.0, "why": "swap 159501 -> 159513 (r1466 verdict X), "
                                                 "sized on the trimmed 372 lots"},
                 {"side": "SELL", "symbol": "513100", "lots": 355, "price": 2.21,
                  "amount_cny": 78455.0, "why": "swap 513100 -> 159513 (r1466 verdict X)"},
                 {"side": "BUY", "symbol": "159513", "lots": 891, "price": 1.76,
                  "amount_cny": 156816.0, "why": "merged buy"}],
             "swap_repricing": [
                 {"leg": "159501", "sibling": "159513", "ordered_lots": 372,
                  "trimmed_lots": 372, "share": 1.0,
                  "gain_published_cny": 5612.5, "gain_on_trimmed_book_cny": 5612.5,
                  "overstated_cny": 0.0},
                 {"leg": "513100", "sibling": "159513", "ordered_lots": 355,
                  "trimmed_lots": 355, "share": 1.0,
                  "gain_published_cny": 4149.3, "gain_on_trimmed_book_cny": 4149.3,
                  "overstated_cny": 0.0}]}
    h20 = {"members": 272, "n": 272, "censored": 0, "median_delta_pp": 0.15,
           "mean_delta_pp": 0.18, "share_narrowed_net_of_toll": 0.27, "share_widened": 0.55}
    conv = {"bar": "2026-11-10", "reference_horizon": 20, "toll_pp": 0.32,
            "pairs": [
                {"leg_symbol": "159501", "sibling_symbol": "159513",
                 "verdict": "DOES_NOT_PAY_MEASURED", "cohort_used": "broad",
                 "notional_cny": 78492.0, "net_after_toll_pp": -0.4705,
                 "net_after_toll_cny": -369.0,
                 "cohorts": {"broad": {"h20": h20}}},
                {"leg_symbol": "513100", "sibling_symbol": "159513",
                 "verdict": "DOES_NOT_PAY_MEASURED", "cohort_used": "broad",
                 "notional_cny": 78455.0, "net_after_toll_pp": -0.2265,
                 "net_after_toll_cny": -178.0,
                 "cohorts": {"broad": {"h20": dict(h20, median_delta_pp=-0.09)}}}]}
    return {"as_of": "2026-11-10", "swap_stack": stack, "swap_convergence": conv}


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    ctx = _fixture()
    f = compute(ctx)

    leg("L1 both legs are paired", len(f["rows"]) == 2, len(f["rows"]))
    row = f["rows"][0]
    leg("L2 the level comes from the stack's own figure, not re-derived",
        abs(row["level_cny"] - 5612.5) < 0.011, row["level_cny"])
    leg("L3 the path comes from the convergence face", abs(row["path_cny"] + 369.0) < 0.011,
        row["path_cny"])
    leg("L4 the discount is expressed as the narrowing it needs",
        abs(row["narrowing_needed_pp"] - 7.15) < 0.011, row["narrowing_needed_pp"])
    leg("L5 no combined number is produced", f["totals"]["combined_cny"] is None, f["totals"])
    leg("L6 the refusal is carried as a sentence, not a blank",
        "两种读法" in (f["sum_refused"] or ""), f["sum_refused"])
    leg("L7 totals add up on each column separately",
        abs(f["totals"]["level_cny"] - 9761.8) < 0.011
        and abs(f["totals"]["path_cny"] + 547.0) < 0.011, f["totals"])
    leg("L8 every path is negative, so the discount is uncollected",
        f["verdict"] == "DISCOUNT_UNCOLLECTED", f["verdict"])
    leg("L9 check is clean on the clean face", check(f) == [], check(f))
    leg("L10 the sentence refuses addition and names the horizon",
        "不能相加" in f["sentence"] and "20" in f["sentence"], f["sentence"][:80])
    leg("L11 md prints both columns and the refusal",
        any("不能相加" in x for x in md_lines(f)) and len(f["rows"]) == 2)

    # a pair whose measured path pays is reported as partly collected, still never summed
    ctx2 = _fixture()
    ctx2["swap_convergence"]["pairs"][0]["net_after_toll_pp"] = 0.28
    ctx2["swap_convergence"]["pairs"][0]["net_after_toll_cny"] = 219.8
    f2 = compute(ctx2)
    leg("L12 one paying pair flips the verdict", f2["verdict"] == "DISCOUNT_PARTLY_COLLECTED",
        f2["verdict"])
    leg("L13 even when both are positive there is no sum",
        f2["totals"]["combined_cny"] is None and check(f2) == [], f2["totals"])

    # the two faces must price the same trade
    ctx3 = _fixture()
    ctx3["swap_convergence"]["pairs"][0]["notional_cny"] = 70000.0
    f3 = compute(ctx3)
    leg("L14 a notional mismatch unpairs the row instead of pricing it",
        len(f3["rows"]) == 1 and any(u["leg_symbol"] == "159501" for u in f3["unpaired"]),
        [u["leg_symbol"] for u in f3["unpaired"]])
    leg("L15 the mismatch is voiced with both amounts",
        any("不同的一笔" in u["why"] for u in f3["unpaired"]), f3["unpaired"])

    # legs present on only one side are named, never priced at zero
    ctx4 = _fixture()
    ctx4["swap_convergence"]["pairs"] = ctx4["swap_convergence"]["pairs"][:1]
    f4 = compute(ctx4)
    leg("L16 a leg with no path is named, not zeroed",
        len(f4["rows"]) == 1 and any(u["leg_symbol"] == "513100" for u in f4["unpaired"]),
        f4["unpaired"])
    ctx5 = _fixture()
    ctx5["swap_stack"]["swap_repricing"] = ctx5["swap_stack"]["swap_repricing"][:1]
    f5 = compute(ctx5)
    leg("L17 a leg with no level is named, not zeroed",
        len(f5["rows"]) == 1 and any(u["leg_symbol"] == "513100" for u in f5["unpaired"]),
        f5["unpaired"])

    # a convergence row that judged nothing is not a reading
    ctx6 = _fixture()
    ctx6["swap_convergence"]["pairs"][0]["verdict"] = "COHORT_TOO_SMALL"
    ctx6["swap_convergence"]["pairs"][0]["why"] = "样太少"
    f6 = compute(ctx6)
    leg("L18 an unjudged path is unpaired", len(f6["rows"]) == 1, len(f6["rows"]))

    # refusals
    ctx7 = _fixture()
    ctx7["swap_convergence"] = None
    leg("L19 a missing convergence face refuses", compute(ctx7)["verdict"] == "CANNOT_PAIR")
    ctx8 = _fixture()
    ctx8["swap_convergence"]["bar"] = "2026-11-11"
    leg("L20 a face from another bar is refused", compute(ctx8)["verdict"] == "CANNOT_PAIR")
    ctx9 = _fixture()
    ctx9["swap_convergence"]["pairs"] = []
    f9 = compute(ctx9)
    leg("L21 nothing pairable is stated, not reported as not paying",
        f9["verdict"] == "CANNOT_PAIR" and "不是「不赚钱」" in f9["sentence"], f9["sentence"])

    # tampering
    f10 = json.loads(json.dumps(f))
    f10["totals"]["combined_cny"] = 9214.8
    leg("L22 check catches a combined number", check(f10) != [], check(f10))
    f11 = json.loads(json.dumps(f))
    f11["rows"][0]["narrowing_needed_pp"] = 8.67
    leg("L23 check catches a narrowing that is not level/notional", check(f11) != [])
    f12 = json.loads(json.dumps(f))
    f12["rows"][0]["path_cny"] = -100.0
    leg("L24 check catches a path that no longer sums to the total", check(f12) != [])
    f13 = json.loads(json.dumps(f))
    f13["rows"][0]["same_trade"] = False
    leg("L25 check catches a priced row whose faces disagreed", check(f13) != [])

    # md: absent and refused faces still say something
    leg("L26 an absent face prints a refusal line",
        any("跑 scripts" in x for x in md_lines(None)))
    ctx10 = _fixture()
    ctx10["swap_convergence"] = None
    leg("L27 a missing face prints its reason",
        any("算不出来" in x for x in md_lines(compute(ctx10))))

    ok = sum(1 for _n, v, _d in legs if v)
    print("etf_book_swap_effect selftest %d/%d" % (ok, len(legs)))
    for n, v, d in legs:
        print("  %-6s %s%s" % ("PASS" if v else "FAIL", n, "" if v else "  :: %r" % (d,)))
    return 0 if ok == len(legs) else 1


def _emit(line):
    """Console-safe print: a GBK terminal must not be able to kill a published face."""
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "backslashreplace").decode("ascii"))


def run():
    stack = _read_json(STACK_FACE)
    conv = _read_json(CONV_FACE)
    as_of = (stack or {}).get("asof") or (conv or {}).get("bar")
    face = compute({"as_of": as_of, "swap_stack": stack, "swap_convergence": conv})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    L = ["# 换进去赚的和换回来量的：一行两个数，不能相加（r1524）", "",
         "bar %s ｜ 判定 **%s**" % (as_of, face["verdict"]), ""]
    L += md_lines(face, heading="## 逐对读数")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    _emit(json.dumps({"verdict": face["verdict"],
                      "rows": len(face.get("rows") or []),
                      "unpaired": len(face.get("unpaired") or []),
                      "level_cny": (face.get("totals") or {}).get("level_cny"),
                      "path_cny": (face.get("totals") or {}).get("path_cny"),
                      "combined_cny": (face.get("totals") or {}).get("combined_cny"),
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
        print("CHECK_OK rows=%d level=%s path=%s combined=%s"
              % (len((face or {}).get("rows") or []),
                 ((face or {}).get("totals") or {}).get("level_cny"),
                 ((face or {}).get("totals") or {}).get("path_cny"),
                 ((face or {}).get("totals") or {}).get("combined_cny")))
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
