"""The trim under the cap has a toll, and the toll is smaller than the gap it chases.

`etf_book_cap_beta_units` answered "43.5% of a beta-0.48 book is 20.94% of the market,
i.e. 0.94pp over a 20% cap, and 19,543 CNY would put it back on the cap -- or 0 CNY if you
read beta over the full history."  It stopped there, because a second reading of the same
word ("trim") had not been priced:

  * **In whole lots.**  A trim in CNY is not an order.  Each of the five names trades in
    100-share lots, so the question is whether 19,543 CNY can be reached in lots at all,
    what it actually raises, and how much of the gap the lot grid leaves behind.
  * **What following the cap costs.**  The beta face publishes a 69-window path.  Read each
    window on its own and the book is over the cap in some of them and inside it in others;
    a manager who obeys the cap window by window sells at every crossing and buys back at
    the next one.  Those round trips have a price, and it is payable in money while the
    thing being chased ("0.94pp over") is inside the ruler's own +/-5.89pp.

So this face prints three things the cap face cannot: the lot-level realisation of today's
trim, its one-way and round-trip cost at the book's own 8bp per side, and the cumulative
cost of obeying the cap along the published path.  Every number is arithmetic on faces that
already exist; no face is rewritten, and no recommendation is made -- the page says what
each number answers and what it does not.

  python scripts/etf_book_cap_trim_toll.py run
  python scripts/etf_book_cap_trim_toll.py --check
  python scripts/etf_book_cap_trim_toll.py --selftest

Outputs:
  results/etf_book_cap_trim_toll.json
  research/ETF_BOOK_CAP_TRIM_TOLL.md
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

OUT = os.path.join(REPO, "results", "etf_book_cap_trim_toll.json")
PAGE = os.path.join(REPO, "research", "ETF_BOOK_CAP_TRIM_TOLL.md")
CAP_FACE = os.path.join(REPO, "results", "etf_book_cap_beta_units.json")
BETA_FACE = os.path.join(REPO, "results", "etf_book_beta_paths.json")

LOT = 100                 # shares per lot, A-share ETF standard
BLOCK_BEGIN = "<!-- CAP-TRIM-BEGIN -->"
BLOCK_END = "<!-- CAP-TRIM-END -->"


# ---------------------------------------------------------------------------------------
# pure helpers -- the selftest holds these without any face on disk
# ---------------------------------------------------------------------------------------
def implied_k(cap, beta):
    """The k a book of this beta must hold to sit exactly on the cap."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    return float(cap) / float(beta)


def over_cny(k_now, cap, beta, nav):
    """CNY of the book that is above the cap at this beta reading.  0 when inside."""
    need = implied_k(cap, beta)
    return max(0.0, (float(k_now) - need) * float(nav))


def toll_cny(amount_cny, cost_bp_per_side, sides=1):
    """Cost of trading `amount_cny` at the book's own per-side bp."""
    return float(amount_cny) * float(cost_bp_per_side) / 10000.0 * int(sides)


def lot_value(row):
    return float(row["price"]) * LOT


def plan_lots(holdings, target_cny):
    """Whole-lot sell plan closest to `target_cny`, proportionally across names.

    Proportional because the ticket holds the five names equal-weight: de-risking the book
    means the same percentage off each name, not picking one to sell.
    """
    book = sum(float(h["amount_cny"]) for h in holdings)
    if book <= 0:
        raise ValueError("book must be positive")
    share = float(target_cny) / book
    rows = []
    for h in holdings:
        lot_cny = lot_value(h)
        want = float(h["amount_cny"]) * share
        lots = int(round(want / lot_cny))
        lots = max(0, min(int(h["lots"]), lots))
        rows.append({"symbol": h["symbol"], "price": float(h["price"]),
                     "lots_held": int(h["lots"]), "lots_sell": lots,
                     "sell_cny": round(lots * lot_cny, 2)})
    # one-lot greedy fix: if we can get closer by moving a single lot, do it (never past
    # the target by more than the closest name's lot value)
    def residual(rws):
        return sum(r["sell_cny"] for r in rws) - float(target_cny)

    best = residual(rows)
    for _ in range(12):
        moved = False
        for r in rows:
            for step in (1, -1):
                if r["lots_sell"] + step < 0 or r["lots_sell"] + step > r["lots_held"]:
                    continue
                r["lots_sell"] += step
                r["sell_cny"] = round(r["lots_sell"] * lot_value(r), 2)
                cand = residual(rows)
                if abs(cand) < abs(best) - 1e-9:
                    best = cand
                    moved = True
                    break
                r["lots_sell"] -= step
                r["sell_cny"] = round(r["lots_sell"] * lot_value(r), 2)
            if moved:
                break
        if not moved:
            break
    total = round(sum(r["sell_cny"] for r in rows), 2)
    largest_lot = max(lot_value(r) for r in rows) if rows else 0.0
    return {"target_cny": round(float(target_cny), 2),
            "sell_cny": total,
            "residual_cny": round(total - float(target_cny), 2),
            "lots_total": sum(r["lots_sell"] for r in rows),
            "largest_lot_cny": round(largest_lot, 2),
            "reachable": abs(total - float(target_cny)) <= largest_lot + 1e-9,
            "rows": rows}


def over_segments(path, k_now, cap, nav):
    """Consecutive runs of windows where the book is over the cap.

    A segment is one 'sell', and the window after its last over-window is one 'buy back',
    because the manager only trades when the reading crosses the line.
    """
    flags = [over_cny(k_now, cap, w["beta"], nav) > 0 for w in path]
    segs = 0
    prev = False
    for f in flags:
        if f and not prev:
            segs += 1
        prev = f
    return segs, flags


def verdict_path(share_over_pct, segments):
    if segments == 0:
        return "THE_CAP_NEVER_BINDS"
    if share_over_pct >= 80.0:
        return "CAP_BINDS_MOST_WINDOWS"
    if share_over_pct >= 20.0:
        return "CAP_BINDS_SOME_WINDOWS"
    return "CAP_BINDS_FEW_WINDOWS"


def verdict_day(gap_cny, band_cny):
    """Today's decision, in the ruler's own units -- same three-state logic as the cap face."""
    if gap_cny <= 0:
        return "NOTHING_TO_TRIM"
    if gap_cny <= abs(band_cny):
        return "TRIM_IS_INSIDE_THE_RULER"
    return "TRIM_IS_A_REAL_BREACH"


# ---------------------------------------------------------------------------------------
# formatting (one place, so the page and --check cannot drift)
# ---------------------------------------------------------------------------------------
def f2(x):
    return "%.2f" % float(x)


def f4(x):
    return "%.4f" % float(x)


def fpp(x):
    return "%.2f" % float(x)


def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_bytes(path):
    with io.open(path, "rb") as fh:
        return fh.read()


def holdings_from_ticket(ticket):
    pos = ticket.get("positions") or {}
    acc = pos.get("accrual") or {}
    last = acc.get("last") or {}
    rows = last.get("holdings") or []
    if rows:
        return rows, last.get("bar") or ""
    ledger_row = (pos.get("ledger_row") or {})
    rows = ledger_row.get("holdings") or []
    return rows, ledger_row.get("bar") or ""


# ---------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------
def build():
    cap_face = read_json(CAP_FACE)
    beta_face = read_json(BETA_FACE)
    facts_cap = cap_face["facts"]
    ticket_path = os.path.join(REPO, cap_face["ticket_file"].replace("/", os.sep))
    ticket = read_json(ticket_path)

    cap = float(facts_cap["cap_now"])
    k_now = float(facts_cap["k_now"])
    nav = float(facts_cap["nav_cny"])
    cost_bp = 8.0
    trim_now = float(facts_cap["trim_cny_now"])
    trim_full = float(facts_cap["trim_cny_full"])
    band_pp = float(facts_cap["ruler_band_pp"])
    band_cny = band_pp / 100.0 * nav

    holdings, hold_bar = holdings_from_ticket(ticket)
    if not holdings:
        raise RuntimeError("ticket carries no holdings: %s" % cap_face["ticket_file"])

    lots = plan_lots(holdings, trim_now)
    tol_one = toll_cny(trim_now, cost_bp, 1)
    tol_rt = toll_cny(trim_now, cost_bp, 2)

    path = beta_face.get("path") or []
    if not path:
        raise RuntimeError("beta face carries no path")
    segs, flags = over_segments(path, k_now, cap, nav)
    overs = [over_cny(k_now, cap, w["beta"], nav) for w in path]
    over_vals = sorted(v for v in overs if v > 0)
    n_over = len(over_vals)
    median_over = over_vals[len(over_vals) // 2] if over_vals else 0.0
    sum_over = sum(overs)
    # a follower trades the whole over-amount at each crossing, both ways
    toll_follow = toll_cny(sum_over, cost_bp, 2)

    facts = {
        "cap": cap,
        "k_now": k_now,
        "nav_cny": nav,
        "cost_bp_per_side": cost_bp,
        "beta_now": float(facts_cap["beta_now"]),
        "beta_full": float(facts_cap["beta_full"]),
        "trim_day_now_cny": round(trim_now, 2),
        "trim_day_full_cny": round(trim_full, 2),
        "two_readings_apart_cny": round(trim_now - trim_full, 2),
        "ruler_band_pp": band_pp,
        "ruler_band_cny": round(band_cny, 2),
        "verdict_day": verdict_day(trim_now, band_cny),
        "holdings_bar": hold_bar,
        "whole_lot": lots,
        "toll": {
            "one_side_cny": round(tol_one, 2),
            "round_trip_cny": round(tol_rt, 2),
            "one_side_bp_of_gap": round(10000.0 * tol_one / trim_now, 4) if trim_now > 0 else 0.0,
            "round_trip_pct_of_gap": round(100.0 * tol_rt / trim_now, 4) if trim_now > 0 else 0.0,
        },
        "path": {
            "n_windows": len(path),
            "n_over": n_over,
            "counterfactual_k": k_now,
            "share_over_pct": round(100.0 * n_over / len(path), 2),
            "median_over_cny": round(median_over, 2),
            "max_over_cny": round(max(overs), 2) if overs else 0.0,
            "segments": segs,
            "sum_over_cny": round(sum_over, 2),
            "toll_if_followed_cny": round(toll_follow, 2),
            "toll_pct_of_sum_over": round(100.0 * toll_follow / sum_over, 4) if sum_over > 0 else 0.0,
            "first_bar": path[0].get("end_bar"),
            "last_bar": path[-1].get("end_bar"),
        },
    }
    facts["verdict_path"] = verdict_path(facts["path"]["share_over_pct"], segs)

    inputs = [CAP_FACE, BETA_FACE, ticket_path]
    digest = hashlib.sha256(b"".join(read_bytes(p) for p in inputs)).hexdigest()

    return {
        "artifact": "results/etf_book_cap_trim_toll.json",
        "doc": "research/ETF_BOOK_CAP_TRIM_TOLL.md",
        "face": "etf_book_cap_trim_toll",
        "evidence_cutoff": cap_face["evidence_cutoff"],
        "ticket_file": cap_face["ticket_file"],
        "inputs": [os.path.relpath(p, REPO).replace(os.sep, "/") for p in inputs],
        "inputs_digest": digest,
        "facts": facts,
        "caveats": [
            "the lot plan is arithmetic on the accrual bar's closes, not an executable order; fills move prices and the cash leg",
            "the path toll assumes the manager sells the whole over-amount at each over-window and buys it back when the reading comes back inside -- a slower follower pays less and chases less",
            "the path section holds TODAY's k constant across history: it measures how sensitive the cap is to the window's beta, not what this book actually held back then",
            "the cap is read as a beta-units target (k = beta_target / beta); read as notional it is a different, larger breach and this face says nothing about that reading",
            "beta is first order and window-dependent: the beta face itself prices the window choice at 1.96pp of k against a 12.24pp ruler",
        ],
    }


# ---------------------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------------------
def render_page(payload):
    fc = payload["facts"]
    wl = fc["whole_lot"]
    to = fc["toll"]
    pa = fc["path"]

    lines = []
    lines.append("# 帽子下这笔 trim 的往返账")
    lines.append("")
    lines.append("上一面（`ETF_BOOK_CAP_BETA_UNITS`）把「这本书是帽子的 2.18 倍」换算成了 β 单位："
                 "43.5%% 的仓位、β 0.48，对市场是 20.94%%，比 20%% 的帽子多 0.94pp，"
                 "而这点差还在尺子自己 ±%.2fpp 的噪声里。它停在「要卖 19,543 元」这句话上——"
                 "可「元」不是能下单的东西，而且**没人算过照着这句话做要付多少钱**。" % fc["ruler_band_pp"])
    lines.append("")
    lines.append("本面补两件事：这 19,543 元在**整手**上落得下吗、落下之后差多少；"
                 "以及沿着 β 面自己那条 %d 窗的路径严格跟帽子走，往返要烧掉多少。" % pa["n_windows"])
    lines.append("")
    lines.append(BLOCK_BEGIN)
    lines.append("| 项 | 读数 |")
    lines.append("|---|---|")
    lines.append("| 帽子（读自市场时钟） | RED / %.1f%% |" % (fc["cap"] * 100))
    lines.append("| 书的仓位 k / NAV | %s / %s 元 |" % (f4(fc["k_now"]), f2(fc["nav_cny"])))
    lines.append("| β（当窗 / 全史） | %s / %s |" % (f4(fc["beta_now"]), f4(fc["beta_full"])))
    lines.append("| 卖到帽上的钱（当窗 β / 全史 β） | %s / %s 元 |"
                 % (f2(fc["trim_day_now_cny"]), f2(fc["trim_day_full_cny"])))
    lines.append("| 两种 β 读法相差 | %s 元 |" % f2(fc["two_readings_apart_cny"]))
    lines.append("| 尺子噪声带（±%.2fpp）折成钱 | ±%s 元 |" % (fc["ruler_band_pp"], f2(fc["ruler_band_cny"])))
    lines.append("| 今天这个决定 | **%s** |" % fc["verdict_day"])
    lines.append("")
    lines.append("## 一、这 19,543 元在整手上落得下吗")
    lines.append("")
    lines.append("五位等权，所以按同一百分比从每名身上减（不是挑一只卖）。持仓按 %s 的收盘价："
                 % fc["holdings_bar"])
    lines.append("")
    lines.append("| 代码 | 价格 | 持有手数 | 卖出手数 | 卖出金额（元） |")
    lines.append("|---|---|---|---|---|")
    for r in wl["rows"]:
        lines.append("| %s | %s | %d | %d | %s |"
                     % (r["symbol"], f4(r["price"]), r["lots_held"], r["lots_sell"], f2(r["sell_cny"])))
    lines.append("| **合计** | | | **%d** | **%s** |" % (wl["lots_total"], f2(wl["sell_cny"])))
    lines.append("")
    lines.append("- 目标 %s 元，整手实得 %s 元，残差 **%s 元**（净值 %.2fbp，%s）"
                 % (f2(wl["target_cny"]), f2(wl["sell_cny"]), f2(wl["residual_cny"]),
                    10000.0 * wl["residual_cny"] / fc["nav_cny"],
                    "可落在最大一手（%s 元）之内" % f2(wl["largest_lot_cny"]) if wl["reachable"]
                    else "超出最大一手，整手网格落不下"))
    lines.append("")
    lines.append("## 二、照着这句话做，要付多少钱")
    lines.append("")
    lines.append("这本书的成本是每边 %.0fbp（票面自己的口径）：" % fc["cost_bp_per_side"])
    lines.append("")
    lines.append("| 动作 | 金额（元） |")
    lines.append("|---|---|")
    lines.append("| 今天卖 %s 元的单边成本 | %s |" % (f2(fc["trim_day_now_cny"]), f2(to["one_side_cny"])))
    lines.append("| 若一个月内 β 回落、再买回（往返） | %s |" % f2(to["round_trip_cny"]))
    lines.append("| 往返成本占这笔差额 | %s%% |" % ("%.4f" % to["round_trip_pct_of_gap"]))
    lines.append("")
    lines.append("成本本身很小。真正的问题不在成本，在这笔差额**是否大于尺子能看见的东西**："
                 "差额 %s 元 vs 噪声带 %s 元——%s"
                 % (f2(fc["trim_day_now_cny"]), f2(fc["ruler_band_cny"]),
                    "差额在噪声之内，严格跟随等于为噪声付钱" if fc["verdict_day"] == "TRIM_IS_INSIDE_THE_RULER"
                    else "差额在噪声之外，这是真超帽"))
    lines.append("")
    lines.append("## 三、沿 β 路径严格跟帽子走，要烧多少")
    lines.append("")
    lines.append("β 面公布了 %d 个窗（%s → %s）。把每个窗的 β 单独读，这本书在其中 **%d 个窗（%s%%）超帽**："
                 % (pa["n_windows"], pa["first_bar"], pa["last_bar"], pa["n_over"], "%.2f" % pa["share_over_pct"]))
    lines.append("")
    lines.append("> **这一节是反事实，不是历史记录。** 它把**今天的仓位 %s** 当作常量套到每个历史窗的 β 上，"
                 "问的是「如果仓位一直是今天这样，当窗 β 会把敞口推到帽上多少」。"
                 "这本书自己的规则是 `k = beta_target / β_full`，β_full 在历史上也会变、k 会跟着变，"
                 "所以下面这些数字**不是**这本书当时真超帽的金额。它们量的是另一件事："
                 "**仓位规则读全史 β（迟钝），帽的检查读当窗 β（灵敏）——两者的差就是这本书自动漂进漂出帽子的幅度。**"
                 % f4(pa["counterfactual_k"]))
    lines.append("")
    lines.append("| 项 | 读数 |")
    lines.append("|---|---|")
    lines.append("| 超帽窗数 / 总窗数 | %d / %d |" % (pa["n_over"], pa["n_windows"]))
    lines.append("| 超帽时中位差额 | %s 元 |" % f2(pa["median_over_cny"]))
    lines.append("| 最大差额 | %s 元 |" % f2(pa["max_over_cny"]))
    lines.append("| 连续超帽段数（= 卖出的次数） | %d |" % pa["segments"])
    lines.append("| 全期累计超额敞口（每次卖出的金额之和） | %s 元 |" % f2(pa["sum_over_cny"]))
    lines.append("| 严格跟随的往返成本 | %s 元（占累计敞口 %.4f%%） |"
                 % (f2(pa["toll_if_followed_cny"]), pa["toll_pct_of_sum_over"]))
    lines.append("| 判词 | **%s** |" % fc["verdict_path"])
    lines.append("")
    lines.append("- 严格跟随者在 %d 个超帽窗里各卖一次（分 %d 段，段末买回），累计交易额 %s 元、往返成本 %s 元；"
                 "它换来的不是收益，而是「每个窗都不超帽」这个属性"
                 % (pa["n_over"], pa["segments"], f2(pa["sum_over_cny"]), f2(pa["toll_if_followed_cny"])))
    lines.append("- 同一本书，窗口选 1 个还是 69 个，会让「超没超帽」从一条线变成一个分布——"
                 "本面公布的是这个分布的宽度，不是某一次的判决")
    lines.append(BLOCK_END)
    lines.append("## 它不声称什么")
    lines.append("")
    lines.append("- 不是可执行订单：整手表是按 %s 收盘价算的算术，真实成交会同时改动手数与现金腿" % fc["holdings_bar"])
    lines.append("- 不是「不必守帽」的辩护：0.94pp 确实在帽上面；本面只是把「按窗跟随」的价格摆出来供读")
    lines.append("- 不是新回测：全部数字由 β 路径面、帽子单位面与票面算术派生")
    lines.append("- 路径成本假设每个窗都把差额整笔卖掉、下一窗整笔买回；更慢的跟随者付得更少、追得也更少")
    lines.append("")
    lines.append("复跑：`python scripts/etf_book_cap_trim_toll.py run`（写面与本块）、"
                 "`--check`（重算逐字比对）、`--selftest`（离线腿）。")
    lines.append("")
    return "\n".join(lines) + "\n"


def split_block(text):
    i = text.find(BLOCK_BEGIN)
    j = text.find(BLOCK_END)
    if i < 0 or j < 0 or j < i:
        raise ValueError("page block markers missing")
    return text[i:j + len(BLOCK_END)]


def write_page(payload):
    body = render_page(payload)
    with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def run():
    payload = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    write_page(payload)
    fc = payload["facts"]
    print("CAP-TRIM-TOLL day=%s gap=%s band=%s lots=%s sell=%s residual=%s roundtrip=%s "
          "over_windows=%d/%d segments=%d toll_follow=%s"
          % (fc["verdict_day"], f2(fc["trim_day_now_cny"]), f2(fc["ruler_band_cny"]),
             fc["whole_lot"]["lots_total"], f2(fc["whole_lot"]["sell_cny"]),
             f2(fc["whole_lot"]["residual_cny"]), f2(fc["toll"]["round_trip_cny"]),
             fc["path"]["n_over"], fc["path"]["n_windows"], fc["path"]["segments"],
             f2(fc["path"]["toll_if_followed_cny"])))
    return 0


def _diff_paths(a, b, prefix=""):
    """Field paths where two payloads disagree -- 'toll' is a section, 'toll.round_trip_cny'
    is the number a reader can go and fix."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out.extend(_diff_paths(a.get(k), b.get(k),
                                   prefix + ("." if prefix else "") + str(k)))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [prefix]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(_diff_paths(x, y, "%s[%d]" % (prefix, i)))
        return out
    return [] if a == b else [prefix]


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    disk = read_json(OUT)
    fresh = build()
    problems = []
    if disk.get("inputs_digest") != fresh["inputs_digest"]:
        problems.append("STALE: inputs_digest moved (%s -> %s)"
                        % (str(disk.get("inputs_digest"))[:12], fresh["inputs_digest"][:12]))
    else:
        if disk.get("facts") != fresh["facts"]:
            diff = _diff_paths(disk.get("facts") or {}, fresh["facts"])
            problems.append("CHECK FAILED: facts disagree on %s" % ", ".join(diff[:6]))
    page = io.open(PAGE, "r", encoding="utf-8").read()
    try:
        block = split_block(page)
    except ValueError as e:
        problems.append("CHECK FAILED: page block unreadable (%s)" % e)
        block = ""
    if block:
        want = split_block(render_page(fresh))
        if block != want:
            problems.append("CHECK FAILED: page block is not what this face renders")
    if problems:
        for p in problems:
            print(p)
        return 3
    print("CHECK OK")
    return 0


# ---------------------------------------------------------------------------------------
# offline selftest
# ---------------------------------------------------------------------------------------
def selftest():
    cases = []

    def leg(name, fn):
        try:
            fn()
            cases.append((name, True, ""))
        except AssertionError as e:
            cases.append((name, False, str(e)))

    def t_implied_k():
        assert abs(implied_k(0.2, 0.4) - 0.5) < 1e-15

    def t_implied_k_bad_beta():
        try:
            implied_k(0.2, 0.0)
        except ValueError:
            return
        raise AssertionError("a zero beta must not divide")

    def t_over_zero_when_inside():
        # k 0.40 of a beta-0.4 book is 0.16, inside a 0.20 cap
        assert over_cny(0.40, 0.2, 0.4, 1e6) == 0.0

    def t_over_positive_when_above():
        # the published case: k 0.435003, beta 0.4814, cap 0.2 -> ~19.5k
        v = over_cny(0.435003, 0.2, 0.48139415749642345, 1e6)
        assert 19000 < v < 20000, v

    def t_over_monotone_in_beta():
        lo = over_cny(0.435, 0.2, 0.45, 1e6)
        hi = over_cny(0.435, 0.2, 0.60, 1e6)
        assert hi > lo

    def t_toll_one_side():
        assert abs(toll_cny(19543.03, 8.0, 1) - 15.634424) < 1e-9

    def t_toll_round_trip_is_double():
        a = toll_cny(19543.03, 8.0, 1)
        b = toll_cny(19543.03, 8.0, 2)
        assert abs(b - 2 * a) < 1e-12

    def t_plan_hits_target_within_a_lot():
        hold = [{"symbol": "A", "price": 1.0, "lots": 1000, "amount_cny": 100000.0},
                {"symbol": "B", "price": 2.0, "lots": 500, "amount_cny": 100000.0}]
        p = plan_lots(hold, 20000.0)
        assert p["reachable"], p
        assert p["sell_cny"] > 0

    def t_plan_never_exceeds_holdings():
        hold = [{"symbol": "A", "price": 1.0, "lots": 10, "amount_cny": 1000.0}]
        p = plan_lots(hold, 999999.0)
        assert p["rows"][0]["lots_sell"] <= 10

    def t_plan_zero_target_sells_nothing():
        hold = [{"symbol": "A", "price": 1.0, "lots": 10, "amount_cny": 1000.0}]
        p = plan_lots(hold, 0.0)
        assert p["lots_total"] == 0 and p["sell_cny"] == 0.0

    def t_plan_bad_book():
        try:
            plan_lots([{"symbol": "A", "price": 1.0, "lots": 0, "amount_cny": 0.0}], 100.0)
        except ValueError:
            return
        raise AssertionError("a zero book must not divide")

    def t_segments_counts_runs():
        # beta above 0.2/0.435003 (~0.4598) is over the cap; 0.45 is inside it
        path = [{"beta": 0.9}, {"beta": 0.9}, {"beta": 0.45}, {"beta": 0.9}, {"beta": 0.9}]
        segs, flags = over_segments(path, 0.435003, 0.2, 1e6)
        assert flags == [True, True, False, True, True], flags
        assert segs == 2, segs

    def t_segments_all_inside():
        path = [{"beta": 0.45}, {"beta": 0.40}]
        segs, flags = over_segments(path, 0.435003, 0.2, 1e6)
        assert segs == 0 and not any(flags)

    def t_verdict_day_inside():
        assert verdict_day(19543.03, 58920.0) == "TRIM_IS_INSIDE_THE_RULER"

    def t_verdict_day_real():
        assert verdict_day(90000.0, 58920.0) == "TRIM_IS_A_REAL_BREACH"

    def t_verdict_day_negative():
        assert verdict_day(-24.27, 58920.0) == "NOTHING_TO_TRIM"

    def t_verdict_path_most():
        assert verdict_path(95.0, 3) == "CAP_BINDS_MOST_WINDOWS"

    def t_verdict_path_never():
        assert verdict_path(0.0, 0) == "THE_CAP_NEVER_BINDS"

    def t_verdict_path_some():
        assert verdict_path(40.0, 2) == "CAP_BINDS_SOME_WINDOWS"

    def t_block_split():
        page = "x\n" + BLOCK_BEGIN + "\nabc\n" + BLOCK_END + "\ny\n"
        assert split_block(page).startswith(BLOCK_BEGIN)
        try:
            split_block("no markers")
        except ValueError:
            return
        raise AssertionError("missing markers must raise")

    for n, f in [("k on the cap is cap over beta", t_implied_k),
                 ("a zero beta is refused", t_implied_k_bad_beta),
                 ("inside the cap overs nothing", t_over_zero_when_inside),
                 ("the published reading is about 19.5k", t_over_positive_when_above),
                 ("a higher beta overs more", t_over_monotone_in_beta),
                 ("8bp of 19,543.03 is 15.63", t_toll_one_side),
                 ("a round trip is two sides", t_toll_round_trip_is_double),
                 ("a lot plan reaches the target within a lot", t_plan_hits_target_within_a_lot),
                 ("a lot plan never sells more than held", t_plan_never_exceeds_holdings),
                 ("a zero target sells nothing", t_plan_zero_target_sells_nothing),
                 ("a zero book is refused", t_plan_bad_book),
                 ("crossings are counted as segments", t_segments_counts_runs),
                 ("a book always inside has no segment", t_segments_all_inside),
                 ("a gap inside the band is not a breach", t_verdict_day_inside),
                 ("a gap beyond the band is a breach", t_verdict_day_real),
                 ("a negative gap means nothing to trim", t_verdict_day_negative),
                 ("the cap binding most windows is named", t_verdict_path_most),
                 ("a cap that never binds is named", t_verdict_path_never),
                 ("a cap binding some windows is named", t_verdict_path_some),
                 ("the page block markers are required", t_block_split)]:
        leg(n, f)
    bad = [c for c in cases if not c[1]]
    for n, ok, why in cases:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
    print("%d/%d legs pass" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "--check":
        sys.exit(cmd_check())
    sys.exit(run())
