"""ETF book -- what the second exchange costs.

r1466 put a swap trigger on the sheet, r1467 netted the action list into one order, r1521
taught the action table to subtract the post-swap book. All three price the swap on the way
IN. None of them prices the way OUT.

The trigger's own criterion answers a different question: it compares today's gap against
`toll_pp = 2 x cost_bp` (sell the leg, buy the sibling) -- "is this swap worth doing at all".
A round trip is four sides: sell the leg, buy the sibling, and later sell the sibling and buy
the leg back. The second half has never been on this sheet, so a reader cannot tell whether
the gap being harvested is two or four times the toll.

So this face prices it on the size that actually traded:

  * the entry cost is repriced on the executed notional, per pair (not on the ordered size);
  * the exit cost is the same arithmetic on the same notional -- prices assumed unchanged,
    which is disclosed rather than assumed away;
  * the round trip is printed as a share of today's gap and of the pair's mean gap, so "the
    toll is 15% of the average opportunity" is readable without a calculator;
  * every refused reading is named -- a missing trigger, a missing cost, a bar mismatch, an
    action row without a reason (a trim is not a swap), or a pair the trigger does not carry.

Usage:
    python scripts/etf_book_swap_toll.py run
    python scripts/etf_book_swap_toll.py --check
    python scripts/etf_book_swap_toll.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_toll.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_toll.md")
STACK_FACE = os.path.join(ROOT, "results", "etf_book_swap_stack.json")
TRIGGER_FACE = os.path.join(ROOT, "results", "etf_book_swap_trigger.json")

ENTRY_SIDES = 2  # sell the leg, buy the sibling
EXIT_SIDES = 2   # sell the sibling, buy the leg back

CAVEATS = [
    "the exit toll is contingent: a standing gap (WINDOW_ALWAYS_OPEN) means the desk may never "
    "trade back, so the second exchange is a price on a decision, not a charge already incurred",
    "both halves are priced on the same close and the same notional: intraday execution moves "
    "the proceeds and the lots, and a re-widened gap moves the notional, not the bp",
    "fees and tracking difference between the two tickers are not modelled; cost_bp_per_side "
    "is the trigger's own constant, imported here rather than restated",
]


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def _refuse(face, why):
    face["verdict"] = "CANNOT_PRICE"
    face["sentence"] = "这一问答不了：%s。" % why
    face["refused"] = why
    return face


def _cost_cny(notional, cost_bp, sides):
    return round(float(notional) * float(cost_bp) / 10000.0 * sides, 2)


def compute(ctx):
    """Price the way out on the notional that actually traded.

    `ctx` carries the already-published faces: {"as_of", "ticket_bar", "swap_stack",
    "swap_trigger"}. Nothing is re-derived from panel bytes here -- this face only does
    arithmetic on numbers another face published, so a disagreement is a bug in one of them,
    not a difference of opinion.
    """
    as_of = ctx.get("as_of")
    face = {"artifact": "etf_book_swap_toll", "bar": as_of, "verdict": None, "rows": [],
            "totals": {}, "sentence": "", "refused": None,
            "sources": {"swap_stack": "results/etf_book_swap_stack.json",
                        "swap_trigger": "results/etf_book_swap_trigger.json"},
            "caveats": list(CAVEATS)}

    stack = ctx.get("swap_stack")
    trig = ctx.get("swap_trigger")
    if not stack:
        return _refuse(face, "没有已发布的净额单面（scripts/etf_book_swap_stack.py run）")
    if not trig:
        return _refuse(face, "没有已发布的换票触发面（脚本缺 face，读不出价差与成本）")

    stack_bar = stack.get("asof")
    if as_of and stack_bar and stack_bar != as_of:
        return _refuse(face, "净额单面停在 %s、这张单是 %s：两个 bar 的数不能相减（r1516 律）"
                       % (stack_bar, as_of))
    ticket_bar = ctx.get("ticket_bar")
    if ticket_bar and as_of and ticket_bar != as_of:
        return _refuse(face, "票面停在 %s、账本 bar 是 %s" % (ticket_bar, as_of))

    criteria = trig.get("criteria") or {}
    cost_bp = criteria.get("cost_bp_per_side")
    if cost_bp is None:
        return _refuse(face, "触发面没有 cost_bp_per_side：成本一旦缺省，往返就是编出来的数")
    cost_bp = float(cost_bp)
    face["cost_bp_per_side"] = cost_bp
    face["started_from"] = as_of or stack_bar

    actions = stack.get("actions") or []
    sells = {}
    for a in actions:
        if (a.get("side") or "").upper() == "SELL":
            sells[str(a.get("symbol"))] = a
    bought = {str(a.get("symbol")) for a in actions
              if (a.get("side") or "").upper() == "BUY"}

    rows, skipped = [], []
    for pair in trig.get("pairs") or []:
        leg = str(pair.get("leg_symbol"))
        sib = str(pair.get("sibling_symbol"))
        act = sells.get(leg)
        if act is None:
            continue
        why = act.get("why") or ""
        if ("swap %s" % leg) not in why:
            # A SELL on this bar whose reason is not a swap is a trim/exit, not a round trip.
            skipped.append({"symbol": leg, "reason": why or "动作行没有写理由"})
            continue
        notional = act.get("amount_cny")
        if not notional:
            skipped.append({"symbol": leg, "reason": "卖出动作没有金额"})
            continue
        entry = _cost_cny(notional, cost_bp, ENTRY_SIDES)
        exit_ = _cost_cny(notional, cost_bp, EXIT_SIDES)
        trip_pp = round((ENTRY_SIDES + EXIT_SIDES) * cost_bp / 100.0, 4)
        today_gap = pair.get("today_gap_pp")
        mean_gap = pair.get("mean_gap_pp")
        expiry = pair.get("expiry") or {}
        median_sessions = expiry.get("median_sessions")
        rows.append({
            "symbol": leg,
            "sibling": sib,
            "lots": act.get("lots"),
            "price": act.get("price"),
            "notional_cny": round(float(notional), 2),
            "sibling_bought_this_bar": sib in bought,
            "entry_sides": ENTRY_SIDES,
            "exit_sides": EXIT_SIDES,
            "entry_cost_cny": entry,
            "exit_cost_cny": exit_,
            "round_trip_cny": round(entry + exit_, 2),
            "round_trip_pp": trip_pp,
            "today_gap_pp": today_gap,
            "share_of_today_gap": (round(trip_pp / today_gap, 4)
                                   if today_gap else None),
            "mean_gap_pp": mean_gap,
            "share_of_mean_gap": (round(trip_pp / mean_gap, 4) if mean_gap else None),
            "median_sessions": median_sessions,
            "toll_pp_per_session": (round(trip_pp / median_sessions, 6)
                                    if median_sessions else None),
            "verdict": pair.get("verdict"),
        })

    face["rows"] = rows
    if skipped:
        face["skipped"] = skipped
    if not rows:
        face["verdict"] = "NO_SWAP_ON_THIS_BAR"
        face["sentence"] = ("这一单没有换票动作，所以没有「换回来」的过路费可报"
                            "（不是 0 元：没有动作就没有第二个交易）。")
        return face

    tot_n = round(sum(r["notional_cny"] for r in rows), 2)
    tot_e = round(sum(r["entry_cost_cny"] for r in rows), 2)
    tot_x = round(sum(r["exit_cost_cny"] for r in rows), 2)
    face["totals"] = {"notional_cny": tot_n, "entry_cost_cny": tot_e,
                      "exit_cost_cny": tot_x, "round_trip_cny": round(tot_e + tot_x, 2)}
    face["verdict"] = "TOLL_PRICED"
    face["sentence"] = sentence(face)
    return face


def _fmt(x):
    return format(x, ",.0f")


def _pct(share):
    return "%.1f%%" % (100.0 * share) if share is not None else "读不出"


def sentence(face):
    t = face.get("totals") or {}
    rows = face.get("rows") or []
    if not rows:
        return face.get("sentence") or ""
    gaps = [r for r in rows
            if r.get("share_of_today_gap") is not None
            or r.get("share_of_mean_gap") is not None]
    tail = ""
    if gaps:
        tail = ("；占今天价差 %s、占各自平均价差 %s"
                % ("/".join(_pct(r.get("share_of_today_gap")) for r in gaps),
                   "/".join(_pct(r.get("share_of_mean_gap")) for r in gaps)))
    return ("这次换票已经付了 ¥%s 的过路费（每一对卖出+买入各 %.0fbp），"
            "如果下一个决策 bar 换回来，同样的钱还要再付一遍 ¥%s——往返合计 ¥%s = %.2fpp%s。"
            % (_fmt(t.get("entry_cost_cny") or 0.0), face.get("cost_bp_per_side") or 0.0,
               _fmt(t.get("exit_cost_cny") or 0.0), _fmt(t.get("round_trip_cny") or 0.0),
               rows[0].get("round_trip_pp") or 0.0, tail))


def md_lines(face, heading="## 换回来要多少钱（r1522）"):
    if not face:
        return ["", heading,
                "- **这一问答不了**：没有已发布的过路费面（跑 "
                "scripts/etf_book_swap_toll.py run）。缺面不等于不用付这笔钱。", ""]
    if face.get("refused"):
        return ["", heading, "- **算不出来**：%s。" % face["refused"],
                "- 读法：这一节只对已发布的数做加减乘除，不猜价差也不猜成本；"
                "「算不出来」与「不用付」是两件事。", ""]
    L = ["", heading, "- %s" % (face.get("sentence") or "")]
    rows = face.get("rows") or []
    if rows:
        L += ["", "| 换出 | 换入 | 手数 | 发生额 | 这一次(进) | 换回来(出) | 往返合计 | 占今日价差 | 占均价差 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| %s | %s | %s | ¥%s | ¥%s | ¥%s | ¥%s | %s | %s |"
                     % (r["symbol"], r["sibling"], r.get("lots") if r.get("lots") is not None else "-",
                        _fmt(r["notional_cny"]), _fmt(r["entry_cost_cny"]),
                        _fmt(r["exit_cost_cny"]), _fmt(r["round_trip_cny"]),
                        _pct(r.get("share_of_today_gap")), _pct(r.get("share_of_mean_gap"))))
        t = face.get("totals") or {}
        L += ["", "合计：动 ¥%s，进 ¥%s、出 ¥%s，往返 **¥%s**。"
              % (_fmt(t.get("notional_cny") or 0.0), _fmt(t.get("entry_cost_cny") or 0.0),
                 _fmt(t.get("exit_cost_cny") or 0.0), _fmt(t.get("round_trip_cny") or 0.0))]
        med = [r for r in rows if r.get("median_sessions")]
        if med:
            L.append("- 按各自的换回中位 %s 个交易日分摊：往返 = %s pp/日。"
                     % ("/".join(str(r["median_sessions"]) for r in med),
                        "/".join("%.4f" % r["toll_pp_per_session"] for r in med)))
        if any(not r.get("sibling_bought_this_bar") for r in rows):
            L.append("- 其中有的换入票这一单没有买入：它已经在账上，此时「进」只有卖出那一边，"
                     "上表按两边计，口径偏保守。")
    elif face.get("verdict") == "NO_SWAP_ON_THIS_BAR":
        L.append("- 本单没有换票动作，所以没有第二个交易要付；这不是「过路费为 0」的结论。")
    if face.get("skipped"):
        L.append("- 未计入的动作：%s。"
                 % "；".join("%s（%s）" % (s["symbol"], s["reason"]) for s in face["skipped"]))
    return L


def check(face):
    problems = []
    if not face:
        return ["no face"]
    if face.get("verdict") == "TOLL_PRICED":
        bp = face.get("cost_bp_per_side")
        for r in face.get("rows") or []:
            want_in = round(r["notional_cny"] * bp / 10000.0 * ENTRY_SIDES, 2)
            want_out = round(r["notional_cny"] * bp / 10000.0 * EXIT_SIDES, 2)
            if abs(want_in - r["entry_cost_cny"]) > 0.011:
                problems.append("%s entry %s != %s" % (r["symbol"], r["entry_cost_cny"], want_in))
            if abs(want_out - r["exit_cost_cny"]) > 0.011:
                problems.append("%s exit %s != %s" % (r["symbol"], r["exit_cost_cny"], want_out))
            if abs(round(r["round_trip_pp"] - (ENTRY_SIDES + EXIT_SIDES) * bp / 100.0, 4)) > 1e-6:
                problems.append("%s round_trip_pp drift" % r["symbol"])
        t = face.get("totals") or {}
        if abs(round(t["entry_cost_cny"] + t["exit_cost_cny"] - t["round_trip_cny"], 2)) > 0.011:
            problems.append("totals do not add up")
    return problems


# ---------------------------------------------------------------- selftest fixtures

def _fixture():
    trig = {"artifact": "etf_book_swap_trigger",
            "criteria": {"cost_bp_per_side": 8.0, "toll_pp": 0.16},
            "pairs": [{"leg_symbol": "159501", "sibling_symbol": "159513",
                       "today_gap_pp": 8.6708, "mean_gap_pp": 2.0621,
                       "expiry": {"median_sessions": 21.0}, "verdict": "WINDOW_ALWAYS_OPEN"},
                      {"leg_symbol": "513100", "sibling_symbol": "159513",
                       "today_gap_pp": 6.2867, "mean_gap_pp": 2.211,
                       "expiry": {"median_sessions": 21.0}, "verdict": "WINDOW_ALWAYS_OPEN"},
                      {"leg_symbol": "159577", "sibling_symbol": "513850",
                       "today_gap_pp": 0.1903, "mean_gap_pp": 0.1787,
                       "expiry": {"median_sessions": 2.0}, "verdict": "NOT_ACTIONABLE"}]}
    stack = {"asof": "2026-11-10", "verdict": "NETTED_WITH_RESIDUE",
             "actions": [{"side": "SELL", "symbol": "159501", "lots": 372, "price": 2.11,
                          "amount_cny": 78492.0,
                          "why": "swap 159501 -> 159513 (r1466 verdict WINDOW_ALWAYS_OPEN), "
                                 "sized on the trimmed 372 lots"},
                         {"side": "SELL", "symbol": "513100", "lots": 355, "price": 2.21,
                          "amount_cny": 78455.0, "why": "swap 513100 -> 159513"},
                         {"side": "BUY", "symbol": "159513", "lots": 891, "price": 1.76,
                          "amount_cny": 156816.0, "why": "merged buy"}]}
    return {"as_of": "2026-11-10", "ticket_bar": "2026-11-10",
            "swap_stack": stack, "swap_trigger": trig}


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    ctx = _fixture()
    f = compute(ctx)

    leg("L1 verdict is TOLL_PRICED on a clean pair", f["verdict"] == "TOLL_PRICED")
    leg("L2 both executed legs priced, the non-actionable pair excluded", len(f["rows"]) == 2)
    r = f["rows"][0]
    leg("L3 round trip is four sides of the same bp", abs(r["round_trip_pp"] - 0.32) < 1e-9)
    leg("L4 entry is two sides of notional",
        abs(r["entry_cost_cny"] - round(78492.0 * 8.0 / 10000.0 * 2, 2)) < 0.011)
    leg("L5 exit equals entry on the same notional",
        abs(r["exit_cost_cny"] - r["entry_cost_cny"]) < 0.011)
    leg("L6 totals add up", abs(f["totals"]["round_trip_cny"]
                                - (f["totals"]["entry_cost_cny"]
                                   + f["totals"]["exit_cost_cny"])) < 0.011)
    leg("L7 today's-gap share is the ratio, not a copy of the bp",
        abs(r["share_of_today_gap"] - round(0.32 / 8.6708, 4)) < 1e-6)
    leg("L8 mean-gap share computed from the pair's own mean",
        abs(r["share_of_mean_gap"] - round(0.32 / 2.0621, 4)) < 1e-6)
    leg("L9 sentence carries the CNY round trip", "\u00a5" in f["sentence"])
    leg("L10 check() is clean on the clean face", check(f) == [])

    # cost is imported, not restated: doubling it doubles the money
    ctx2 = _fixture()
    ctx2["swap_trigger"] = json.loads(json.dumps(ctx["swap_trigger"]))
    ctx2["swap_trigger"]["criteria"]["cost_bp_per_side"] = 16.0
    f2 = compute(ctx2)
    leg("L11 doubling the imported cost doubles the toll",
        abs(f2["totals"]["round_trip_cny"] - 2 * f["totals"]["round_trip_cny"]) < 0.021)

    # bar mismatch refuses
    ctx3 = _fixture()
    ctx3["as_of"] = "2026-11-11"
    f3 = compute(ctx3)
    leg("L12 a stack from another bar is refused, not rescaled",
        f3["verdict"] == "CANNOT_PRICE" and "bar" in (f3.get("refused") or ""))

    # a trim is not a swap
    ctx4 = _fixture()
    ctx4["swap_stack"]["actions"][0]["why"] = "floor trim 159501 to 372 lots"
    f4 = compute(ctx4)
    leg("L13 a SELL without a swap reason is skipped and named",
        len(f4["rows"]) == 1 and any(s["symbol"] == "159501" for s in (f4.get("skipped") or [])))

    # no swap at all
    ctx5 = _fixture()
    ctx5["swap_stack"]["actions"] = []
    f5 = compute(ctx5)
    leg("L14 no action -> NO_SWAP_ON_THIS_BAR, not a zero-price claim",
        f5["verdict"] == "NO_SWAP_ON_THIS_BAR"
        and "没有第二个交易" in f5["sentence"])

    # missing cost refuses
    ctx6 = _fixture()
    del ctx6["swap_trigger"]["criteria"]["cost_bp_per_side"]
    f6 = compute(ctx6)
    leg("L15 missing cost_bp refuses", f6["verdict"] == "CANNOT_PRICE")

    # missing trigger refuses
    ctx7 = _fixture()
    ctx7["swap_trigger"] = None
    leg("L16 missing trigger refuses", compute(ctx7)["verdict"] == "CANNOT_PRICE")

    # tampered arithmetic is caught by check()
    f8 = json.loads(json.dumps(f))
    f8["rows"][0]["entry_cost_cny"] += 5.0
    leg("L17 check catches a tampered entry cost", check(f8) != [])

    # md: absent face prints a line, never a silent pass
    md0 = md_lines(None)
    leg("L18 absent face prints a refusal line", any("算不了" in x or "跑 scripts" in x for x in md0))
    md = md_lines(f)
    leg("L19 md carries the round-trip total", any("往返" in x for x in md))
    md5 = md_lines(f5)
    leg("L20 md explains a zero-action sheet", any("没有换票动作" in x for x in md5))

    # a gap that is missing must print as unreadable, not as 0%
    ctx9 = _fixture()
    ctx9["swap_trigger"]["pairs"][0]["today_gap_pp"] = None
    f9 = compute(ctx9)
    leg("L21 an unreadable gap is None and prints as unreadable",
        f9["rows"][0]["share_of_today_gap"] is None
        and any("读不出" in x for x in md_lines(f9)))

    ok = sum(1 for _, v in legs if v)
    print("etf_book_swap_toll selftest %d/%d" % (ok, len(legs)))
    for n, v in legs:
        print("  %-6s %s" % ("PASS" if v else "FAIL", n))
    return 0 if ok == len(legs) else 1


def _stack_face():
    return _read_json(STACK_FACE)


def _trigger_face():
    trig = _read_json(TRIGGER_FACE)
    return trig


def run():
    stack = _stack_face()
    trig = _trigger_face()
    as_of = (stack or {}).get("asof")
    if not as_of:
        ticket = _read_json(os.path.join(ROOT, "results", "etf_book_order", "latest.json"))
        as_of = (ticket or {}).get("as_of")
    face = compute({"as_of": as_of, "ticket_bar": as_of,
                    "swap_stack": stack, "swap_trigger": trig})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    lines = ["# 换回来要多少钱（r1522）", "", "bar %s ｜ 判定 **%s**"
             % (as_of, face["verdict"]), ""]
    lines += md_lines(face, heading="## 逐对读数")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(json.dumps({"verdict": face["verdict"], "rows": len(face.get("rows") or []),
                      "round_trip_cny": (face.get("totals") or {}).get("round_trip_cny"),
                      "sentence": face.get("sentence")}, ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
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
        n = len((face or {}).get("rows") or [])
        print("CHECK_OK rows=%d" % n)
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
