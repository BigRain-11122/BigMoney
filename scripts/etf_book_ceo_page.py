"""ETF production book -> CEO one-page (docs/live_book/LIVE-BOOK-YYYYMMDD.md + .json).

Why this exists: the ETF book is the only money-making structure this company has
shown to work, but every face it publishes (ticket JSON, card JSON, registry JSON,
forward ledger) is machine-shaped. Nothing in the repo answers, in plain language,
"what do I buy today, with how much money, how am I doing, and when does it change".

Pure aggregation, zero new judgement:
  - order list / money split   <- results/etf_book_order/latest.json -> ticket file
  - backtest expectation band  <- results/etf_book_production/latest.json (card)
  - forward track vs inception <- results/etf_book_forward/LEDGER.json
  - next rebalance date        <- data/exchange_calendar.csv (official calendar)

Idempotent: same day -> same content; other days' pages are never touched.

Usage:
  python scripts/etf_book_ceo_page.py run
  python scripts/etf_book_ceo_page.py selftest
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "live_book")
TICKET_PTR = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
CARD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

# Single writer: the page is a plain-language mirror of shared artefacts, so two
# machines regenerating the same day would only produce a git race on docs/live_book.
# bm-a prints it; every other host says so and writes nothing (R31 lane-guard lineage).
HOST = "bm-a"


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def writer_allowed(mid):
    return mid == HOST

CLASS_ZH = {
    "equity": "A股",
    "crossborder": "跨境",
    "commodity": "商品",
    "convertible": "转债",
    "bond": "债券",
    "money": "货币",
}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_ticket():
    """Pointer -> the dated ticket file it names."""
    ptr = _load(TICKET_PTR)
    rel = ptr.get("ticket_file") or ptr.get("file") or ptr.get("path")
    if isinstance(rel, str) and rel:
        cands = [rel] if os.path.isabs(rel) else [
            os.path.join(os.path.dirname(TICKET_PTR), rel),   # sibling of the pointer
            os.path.join(ROOT, rel),                          # repo-root relative
        ]
        for cand in cands:
            if os.path.exists(cand):
                return ptr, _load(cand), cand
    # fall back to the pointer itself when it already carries the ticket body
    if "ticket" in ptr:
        return ptr, ptr, TICKET_PTR
    raise FileNotFoundError("ticket body not resolvable from %s" % TICKET_PTR)


def trading_days_after(cal_dates, anchor, n):
    """The n-th trading day strictly after `anchor` (ISO strings, sorted asc)."""
    if anchor is None or n is None or int(n) <= 0:
        return None
    later = [d for d in cal_dates if d > anchor]
    if len(later) < int(n):
        return None
    return later[int(n) - 1]


def calendar_dates(path=CAL):
    out = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            s = line.strip()
            if s:
                out.append(s[:10])
    return out


def money_cny(tk, nav):
    """Backtest percentages -> yuan on this ticket's own capital.

    Pure unit change: every number is one already published on the ticket times `nav`.
    Anything unreadable stays None -- a 0 here would read as "this book earns nothing".
    """
    tk = tk or {}
    metrics = tk.get("metrics") or {}
    book = metrics.get("book") or {}
    bench = metrics.get("same_beta_benchmark") or {}
    out = {"capital_cny": round(float(nav or 0.0), 2), "expected_annual_cny": None,
           "benchmark_annual_cny": None, "excess_annual_cny": None,
           "worst_drawdown_cny": None, "basis": None}
    if not nav or not book:
        return out
    out["expected_annual_cny"] = round(float(book["cagr"]) * nav, 0)
    out["worst_drawdown_cny"] = round(float(book["maxdd"]) * nav, 0)
    out["basis"] = "backtest cagr/maxdd x this ticket's capital, no new assumption"
    if bench and metrics.get("excess_pp") is not None:
        out["benchmark_annual_cny"] = round(float(bench["cagr"]) * nav, 0)
        out["excess_annual_cny"] = round(float(metrics["excess_pp"]) / 100.0 * nav, 0)
    return out


def build():
    ptr, tk, tk_path = _load_ticket()
    card = _load(CARD) if os.path.exists(CARD) else {}
    ledger = _load(LEDGER) if os.path.exists(LEDGER) else {}

    nav = float(tk.get("ticket", {}).get("nav") or 0.0)
    order = list(tk.get("ticket", {}).get("order") or [])
    cash_amt = float(tk.get("ticket", {}).get("cash_amount") or 0.0)
    book_amt = float(tk.get("ticket", {}).get("book_amount") or 0.0)
    cash_w = float(tk.get("ticket", {}).get("cash_weight") or 0.0)
    cash_leg = tk.get("ticket", {}).get("cash_leg") or "cash (no instrument named)"

    bars = list(ledger.get("bars") or [])
    fwd = {"bars": len(bars), "inception": None, "nav": None, "since_inception_pct": None,
           "as_of": None}
    if bars:
        fwd["inception"] = bars[0].get("bar")
        fwd["as_of"] = bars[-1].get("bar")
        fwd["nav"] = bars[-1].get("nav")
        fwd["since_inception_pct"] = round((float(bars[-1]["nav"]) - 1.0) * 100.0, 4)

    bt = (card.get("backtest") or {})
    band = {}
    # the executable ticket prices its own book; quote that口径 first, from the ticket itself
    tk_book = (tk.get("metrics") or {}).get("book") or {}
    if tk_book:
        band["%d 名·可执行单口径（本单这份账）" % (tk.get("n_hold") or len(order))] = {
            "full": {"cagr_pct": round(tk_book["cagr"] * 100, 2),
                     "sharpe": round(tk_book["sharpe"], 2),
                     "maxdd_pct": round(tk_book["maxdd"] * 100, 2)}}
    for key, label in (("n5_base", "5 名·beta 覆盖"),
                       ("n12_vt08", "12 名·8% 波动目标（生产卡片口径）")):
        blk = bt.get(key) or {}
        if not blk:
            continue
        row = {}
        for seg in ("full", "is", "oos"):
            s = blk.get(seg) or {}
            if s:
                row[seg] = {"cagr_pct": round(s["cagr"] * 100, 2),
                            "sharpe": round(s["sharpe"], 2),
                            "maxdd_pct": round(s["maxdd"] * 100, 2)}
        band[label] = row

    # the same percentages expressed in yuan on THIS ticket's capital -- a unit change, not a new estimate
    money = money_cny(tk, nav)

    feed = tk.get("feed_status") or {}
    agree = tk.get("card_agreement") or {}
    cal = calendar_dates() if os.path.exists(CAL) else []
    next_reb = trading_days_after(cal, tk.get("evidence_cutoff"), tk.get("next_decision_bars"))
    today = dt.date.today().isoformat()

    page = {
        "schema": "etf-book-ceo-page/v1",
        "generated_for_date": today,
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "priced_bar": feed.get("ticket_bar"),
        "feed_status": feed.get("status"),
        "feed_lag_days": feed.get("lag_days"),
        "capital_cny": nav,
        "book_amount_cny": round(book_amt, 2),
        "cash_amount_cny": round(cash_amt, 2),
        "cash_weight": round(cash_w, 4),
        "cash_leg": cash_leg,
        "k_now": tk.get("k_now"),
        "n_hold": tk.get("n_hold"),
        "cost_bp_per_side": tk.get("cost_bp_per_side"),
        "book_decided_at": tk.get("book_decided_at"),
        "next_decision_bars": tk.get("next_decision_bars"),
        "next_rebalance_date": next_reb,
        "order": [{"symbol": o.get("symbol"), "class": o.get("class"),
                   "class_zh": CLASS_ZH.get(o.get("class"), o.get("class")),
                   "weight": o.get("weight"), "price": o.get("price"),
                   "lots": o.get("lots"), "shares": o.get("shares"),
                   "amount_cny": o.get("amount")} for o in order],
        "forward": fwd,
        "backtest_band": band,
        "excess_pp": (tk.get("metrics") or {}).get("excess_pp"),
        "money_cny": money,
        "ticket_book": tk_book or None,
        "same_beta_benchmark": (tk.get("metrics") or {}).get("same_beta_benchmark"),
        "agreement": {"same_decision_bar": agree.get("same_decision_bar"),
                      "same_priced_bar": agree.get("same_priced_bar"),
                      "card_names": agree.get("card_names")},
        "sources": {"ticket": os.path.relpath(tk_path, ROOT),
                    "card": "results/etf_book_production/latest.json",
                    "ledger": "results/etf_book_forward/LEDGER.json",
                    "calendar": "data/exchange_calendar.csv"},
        "caveats": [
            "回测票池是现存 ETF（有幸存者偏差）；2020-2023 段弱、收益主要集中在 2024 之后。",
            "前向账本只有 %d 个交易日，自起始净值 %.4f 不构成业绩记录。" % (fwd["bars"], fwd["nav"] or 0.0),
            "现金腿若不下单，账本按 %s 计息；不买逆回购则实际是 0 息。" % cash_leg,
            "这是研究产出，不是投资建议；实盘下单是 CEO 的直接权限，公司自动实盘仍是 CEO 唯一门。",
        ],
    }
    return page, today


def render_md(p):
    L = []
    add = L.append
    add("# 今日 ETF 实盘单 —— %s" % p["generated_for_date"])
    add("")
    add("> 一页纸，全部数字从机器面直接抄来：单子来自可执行票、预期来自生产卡片、账面来自前向账本。没有新增判断。")
    add("")
    add("## 一句话")
    inv = p["book_amount_cny"]
    add("今天按下面的清单下单：花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，剩下的 **¥%s**（%.1f%%）放%s。"
        % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
           format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"]))
    add("")
    add("## 下单清单")
    add("")
    add("| 代码 | 类别 | 份（100 股/份） | 参考价 | 金额 |")
    add("|---|---|---|---|---|")
    for o in p["order"]:
        add("| %s | %s | %s | %s | ¥%s |"
            % (o["symbol"], o["class_zh"] or "", format(o["lots"] or 0, ","),
               o["price"], format(o["amount_cny"] or 0, ",.0f")))
    add("| — | **合计** | | | **¥%s** |" % format(p["book_amount_cny"], ",.0f"))
    add("")
    add("剩余现金 ¥%s 买 %s（或等价），不要留活期。" % (format(p["cash_amount_cny"], ",.0f"), p["cash_leg"]))
    add("")
    add("## 账面与节奏")
    add("")
    add("- 定价用的收盘日：**%s**（数据状态 %s，滞后 %s 个交易日）"
        % (p["priced_bar"], p["feed_status"], p["feed_lag_days"]))
    add("- 这套组合上一次定稿：**%s**" % p["book_decided_at"])
    add("- 下次换仓：**%s**（还有 %s 个交易日）" % (p["next_rebalance_date"], p["next_decision_bars"]))
    fwd = p["forward"]
    if fwd["nav"]:
        add("- 前向账本：起始 %s 净值 1.0000 -> %s 净值 **%.4f**（%+.2f%%），共 %d 个交易日"
            % (fwd["inception"], fwd["as_of"], fwd["nav"], fwd["since_inception_pct"], fwd["bars"]))
        add("  - 这只是起步，不能当业绩看。")
    else:
        add("- 前向账本：尚未起算")
    add("")
    add("## 该期待什么（回测口径，扣成本后）")
    add("")
    add("| 组合口径 | 全窗年化 | 夏普 | 最大回撤 | 2020-2023 | 2024 起 |")
    add("|---|---|---|---|---|---|")
    for label, row in p["backtest_band"].items():
        def g(seg, k):
            v = (row.get(seg) or {}).get(k)
            return "—" if v is None else ("%.2f%%" % v if k == "cagr_pct" else
                                          ("%.2f%%" % v if k == "maxdd_pct" else "%.2f" % v))
        add("| %s | %s | %s | %s | %s | %s |"
            % (label, g("full", "cagr_pct"), g("full", "sharpe"), g("full", "maxdd_pct"),
               g("is", "cagr_pct"), g("oos", "cagr_pct")))
    add("")
    add("三行是同一套选券信号，区别只在名数和杠杆规则：第一行是你要下的这份账（5 名 + beta 覆盖 + 8bp 成本）；另两行是生产卡片跑的对照口径。同一决策日，票是卡片的子集。")
    add("")
    add("表里 \u2014 = 该口径没有拆 IS/OOS 分段，不是零。")
    if p.get("excess_pp") is not None and p.get("same_beta_benchmark") and p.get("ticket_book"):
        b = p["same_beta_benchmark"]
        bk = p["ticket_book"]
        add("")
        add("关键一句：**在同样的风险敞口下（beta 基准年化 %.2f%%、夏普 %.2f），这本账回测年化 %.2f%%、夏普 %.2f，多赚 %.2f 个百分点/年**——超额来自选券，不是来自加杠杆。"
            % (b["cagr"] * 100, b["sharpe"], bk["cagr"] * 100, bk["sharpe"], p["excess_pp"]))
    add("")
    add("## 换成年内能赚多少钱（按本单资金 ¥%s）" % format(p["money_cny"]["capital_cny"], ",.0f"))
    add("")
    add("同一批数字再换一把尺子，只做单位换算，不叠加任何新假设：")
    add("")
    add("| 项目 | 一年多少钱 | 怎么来的 |")
    add("|---|---|---|")
    mc = p["money_cny"]

    def y(v):
        return "—" if v is None else ("%s¥%s" % ("+" if v > 0 else "-", format(abs(v), ",.0f")))

    add("| 这本账回测期望 | %s | 年化 %s%% × 资金 |"
        % (y(mc["expected_annual_cny"]), "%.2f" % (p["ticket_book"]["cagr"] * 100) if p.get("ticket_book") else "—"))
    add("| 同风险基准（beta 覆盖） | %s | 基准年化 %s%% × 资金 |"
        % (y(mc["benchmark_annual_cny"]),
           "%.2f" % (p["same_beta_benchmark"]["cagr"] * 100) if p.get("same_beta_benchmark") else "—"))
    add("| **超额部分** | **%s** | 多赚 %.2f 个百分点 × 资金 |"
        % (y(mc["excess_annual_cny"]), p["excess_pp"] or 0.0))
    add("| 一次最坏回撤要亏 | %s | 最大回撤 %s%% × 资金 |"
        % (y(mc["worst_drawdown_cny"]),
           "%.2f" % (p["ticket_book"]["maxdd"] * 100) if p.get("ticket_book") else "—"))
    add("")
    add("读法：一年赚多少是回测期望，不是承诺；最坏回撤那一行才是你要能扛住的数。")
    add("")
    add("## 必须记住的四条")
    add("")
    for c in p["caveats"]:
        add("- " + c)
    add("")
    add("---")
    add("*生成脚本 scripts/etf_book_ceo_page.py｜证据截止 %s｜卡片与单子同一决策日=%s，同一定价日=%s*"
        % (p["evidence_cutoff"], p["agreement"]["same_decision_bar"], p["agreement"]["same_priced_bar"]))
    return "\n".join(L) + "\n"


def run():
    mid = machine_id()
    if not writer_allowed(mid):
        print("etf_book_ceo_page: host=%s is not the writer (host=%s) -- honest no-op, nothing written"
              % (mid, HOST))
        return 0
    page, today = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.md" % today.replace("-", ""))
    js_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.json" % today.replace("-", ""))
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(page))
    with open(js_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(page, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # stable pointer for consumers that should not care about the date
    ptr = os.path.join(OUT_DIR, "latest.json")
    with open(ptr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"generated_for_date": today,
                   "page": os.path.relpath(md_path, ROOT).replace("\\", "/"),
                   "json": os.path.relpath(js_path, ROOT).replace("\\", "/")},
                  fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("LIVE-BOOK written: %s (order %d names, book %.0f, cash %.0f, next rebalance %s)"
          % (os.path.relpath(md_path, ROOT), len(page["order"]), page["book_amount_cny"],
             page["cash_amount_cny"], page["next_rebalance_date"]))
    return 0


def selftest():
    ok = 0
    total = 0

    def chk(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[%d/%d] PASS %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        else:
            print("[%d/%d] FAIL %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        return cond

    # 1. next-rebalance arithmetic on a hand fixture: the 3rd trading day after Fri
    cal = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    chk("L1 calendar: 3rd trading day after 2026-10-23", trading_days_after(cal, "2026-10-23", 3) == "2026-10-28",
        trading_days_after(cal, "2026-10-23", 3))
    chk("L2 calendar: anchor itself never counts", trading_days_after(cal, "2026-10-26", 1) == "2026-10-27")
    chk("L3 calendar: past the end -> None not a guess", trading_days_after(cal, "2026-10-26", 9) is None)
    chk("L4 calendar: degenerate n -> None", trading_days_after(cal, "2026-10-26", 0) is None)

    # 5. the live page's money must add up: order amounts + cash == capital
    page, _today = build()
    s = sum(float(o["amount_cny"] or 0) for o in page["order"])
    chk("L5 money: order sum + cash == capital",
        abs(s + page["cash_amount_cny"] - page["capital_cny"]) < 1.0,
        "sum %.2f + cash %.2f vs nav %.2f" % (s, page["cash_amount_cny"], page["capital_cny"]))
    chk("L6 money: book share == k_now", abs(page["book_amount_cny"] / page["capital_cny"] - page["k_now"]) < 0.002,
        "%.4f vs %.4f" % (page["book_amount_cny"] / page["capital_cny"], page["k_now"]))
    chk("L7 order non-empty and every row has a lot count",
        bool(page["order"]) and all((o["lots"] or 0) > 0 for o in page["order"]), "%d rows" % len(page["order"]))

    # 8. the page must actually say the things a human needs
    md = render_md(page)
    need = ["下单清单", "下次换仓", "该期待什么", "必须记住的四条"]
    missing = [k for k in need if k not in md]
    chk("L8 render: all required sections present", not missing, "missing=%s" % missing)
    chk("L9 render: no unformatted template leftovers", "{:" not in md and "%s" not in md and "%%" not in md)
    chk("L10 render: caveats carried onto the page",
        all(c.split("；")[0][:12] in md for c in page["caveats"]))
    chk("L11 page: next rebalance is a real calendar date",
        isinstance(page["next_rebalance_date"], str) and len(page["next_rebalance_date"]) == 10,
        str(page["next_rebalance_date"]))

    # 12. staleness is quoted, not hidden
    chk("L12 page: data freshness stated", page["feed_status"] is not None and page["priced_bar"] is not None,
        "%s lag=%s" % (page["feed_status"], page["feed_lag_days"]))

    # 13. the money block must be a pure unit change of numbers already on the page
    mc = page["money_cny"]
    tk_book = page.get("ticket_book") or {}
    exp_ok = (abs(mc["expected_annual_cny"] - tk_book["cagr"] * page["capital_cny"]) < 1.0
              if mc["expected_annual_cny"] is not None else mc["expected_annual_cny"] is None)
    chk("L13 money: annual yuan == backtest cagr x capital", exp_ok,
        "%s vs %.2f" % (mc["expected_annual_cny"], tk_book.get("cagr", 0) * page["capital_cny"]))
    chk("L14 money: excess yuan == excess_pp x capital",
        mc["excess_annual_cny"] is not None
        and abs(mc["excess_annual_cny"] - (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]) < 1.0,
        "%s vs %s" % (mc["excess_annual_cny"], (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]))
    chk("L15 money: absent inputs give None, never a zero that would read as 'earns nothing'",
        money_cny({}, 0.0)["expected_annual_cny"] is None
        and money_cny({}, 1000000.0)["excess_annual_cny"] is None
        and money_cny({"metrics": {"book": {"cagr": 0.1, "maxdd": -0.05}}}, 0.0)["expected_annual_cny"] is None,
        "empty ticket -> None; ticket without capital -> None")

    # 16. single writer: only the host may write, and an unknown host must not write either
    chk("L16 guard: writer_allowed('bm-a') only",
        writer_allowed("bm-a") and not writer_allowed("bm-c") and not writer_allowed("bm-b")
        and not writer_allowed(None), "host=%s" % HOST)

    print("\nSummary: %d/%d PASS%s" % (ok, total, "" if ok == total else " -- %d FAIL" % (total - ok)))
    return 0 if ok == total else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        raise SystemExit(run())
    if cmd == "selftest":
        raise SystemExit(selftest())
    print("usage: etf_book_ceo_page.py [run|selftest]")
    raise SystemExit(2)