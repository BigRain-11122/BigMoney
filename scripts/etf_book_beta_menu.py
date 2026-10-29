"""ETF composite book -- today's ticket at every risk tier, on one page.

Why this exists: the book is sold at a *chosen* beta (target/beta_hat, de-risking only),
and the CEO page states one tier at a time. r1147 published the tier table (what each
beta returned), but "what do I actually buy at 0.30 instead of 0.20" still required
re-running the order script with `--beta` and reading two different files.

This script answers it in one command: same panel, same decision bar, same 20-bar grid --
only the de-risking multiplier changes -- so the four tickets are comparable line by line.

Reads (never recomputes) the published forward numbers in
results/etf_book_return_regime.json for expected return / drawdown per tier, and says
`None` when that face is missing instead of inventing a number.

Outputs:
  results/etf_book_beta_menu/MENU-<asof>.json   per-tier tickets + published stats
  docs/live_book/TICKET-MENU-<asof>.md          one page, one table per tier
  results/etf_book_beta_menu/latest.json        pointer to the newest menu

Exploratory: not a verdict, not investment advice, no ledger booking.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F            # noqa: E402
from scripts import etf_phase_beta_target as BT     # noqa: E402
from scripts import etf_book_order as O             # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts.etf_asset_class import classify        # noqa: E402
from scripts.etf_book_ceo_page import stress_stats  # noqa: E402
from config import PATHS                            # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_beta_menu")
DOC_DIR = os.path.join(BASE, "docs", "live_book")
REGIME_JSON = os.path.join(PATHS.results_dir, "etf_book_return_regime.json")
STRESS_DIR = os.path.join(OUT_DIR, "stress")
STRESS_WINDOWS = (1, 5, 20)

# Single writer, same lane as the CEO page it must agree with: docs/live_book/ is bm-a's
# face, so two hosts regenerating the menu would only produce a git race (R31 lineage).
MACHINE = os.path.join(BASE, "fleet", "machine.json")
HOST = "bm-a"


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def writer_allowed(mid):
    return mid == HOST

# the tiers named by r1147; kept in one place so page and tickets cannot disagree
BETAS = (0.10, 0.20, 0.30, 0.50)
NAV = 1_000_000.0


# ------------------------------------------------------------------ published stats
def published_tiers(path=REGIME_JSON):
    """beta -> {cagr_pct, sharpe, maxdd_pct} from the return-regime face, or {} if absent.

    Only the `observed` regime row is used: today's rate and zero-rate are alternate
    cash-rate assumptions, not alternate tiers.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    out = {}
    for cell in d.get("cells") or []:
        if cell.get("regime") != "observed":
            continue
        b = cell.get("beta")
        if b is None:
            continue
        out[round(float(b), 4)] = {"cagr_pct": cell.get("cagr_pct"),
                                   "sharpe": cell.get("sharpe"),
                                   "maxdd_pct": cell.get("maxdd_pct"),
                                   "cash_share": cell.get("cash_share"),
                                   "bars": cell.get("bars"),
                                   "last_bar": cell.get("last_bar")}
    return out


# ------------------------------------------------------------------------ ticket menu
def ticket_menu(score, close, dec_bar, k_by_beta, nav=NAV, classes=None, n_hold=O.N_HOLD):
    """One whole-lot ticket per tier, all ranked on the SAME decision bar."""
    rows = []
    for beta in sorted(k_by_beta):
        k = k_by_beta[beta]
        tk = None if (dec_bar is None or k is None) else O.build_ticket(
            score.loc[dec_bar], close.loc[dec_bar], k, nav, n_hold=n_hold, classes=classes)
        rows.append({"beta": float(beta), "k": None if k is None else round(float(k), 6),
                     "ticket": tk})
    return rows


# ------------------------------------------------------------------------- risk in money
def tier_stress(menu, close, capital, priced_bar, cache_dir=STRESS_DIR,
                windows=STRESS_WINDOWS):
    """Worst N-day window for EACH tier, in percent and in yuan, on one shared panel.

    The menu already prices what each tier buys and what it returned; it does not say
    what a bad month costs. Scaling k does not scale the answer: the windows are
    compounded, so a 0.5x book does not lose exactly half of a 1.0x book's worst 20 days.
    Every tier is therefore walked separately through the same arithmetic the CEO page
    uses (stress_stats), rather than multiplied afterwards.

    Cached per priced bar + capital: the answer only moves when the panel or the ticket
    does, and re-walking the panel every tick is cost without information. Absent panel
    -> None per tier, never a zero.
    """
    cache = os.path.join(cache_dir, "STRESS-%s-%d-%s.json" % (
        str(priced_bar).replace("-", ""), int(round(float(capital or 0.0))),
        "_".join(str(int(w)) for w in windows)))
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as fh:
                c = json.load(fh)
            if c.get("priced_bar") == str(priced_bar):
                # JSON turns the beta keys into strings; the caller keys by number
                return {float(k): v for k, v in (c.get("tiers") or {}).items()}
        except (OSError, ValueError):
            pass
    out = {}
    try:
        if close is None:
            return {float(r["beta"]): None for r in menu}
        legs_all = {}
        for r in menu:
            tk = r.get("ticket") or {}
            legs = {}
            for n in tk.get("order") or []:
                sym = n.get("symbol")
                w = float(n.get("weight") or 0.0)
                if sym in close.columns:
                    legs[sym] = close[sym].astype(float).pct_change().fillna(0.0) * w
                else:
                    legs[sym] = pd.Series(0.0, index=close.index)
            legs_all[float(r["beta"])] = legs
        for beta, legs in legs_all.items():
            book = pd.DataFrame(legs).sum(axis=1) if legs else None
            out[beta] = stress_stats(book, windows=windows, capital=capital)
    except Exception:
        return {float(r["beta"]): None for r in menu}
    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"priced_bar": str(priced_bar), "capital_cny": capital,
                       "tiers": out}, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    except OSError:
        pass
    return out


def render(menu, asof, dec_bar, nav, caveats):
    L = ["# 今天的票：四个风险档各买什么（%s）" % asof, ""]
    L += ["同一套引擎、同一批票、同一个决策日 **%s**、同样 %d 个交易日换仓与 8bp 成本；"
          % (dec_bar, O.REBAL), "唯一变动的是降险系数 k = 目标β / 实际β（只降不升杠杆）。",
          "名义本金 ¥%s。" % f"{nav:,.0f}", ""]
    L += ["| 目标β | 实际 k | 买股票 | 留现金 | 回测年化 | 回测回撤 | 夏普 |",
          "|---|---|---|---|---|---|---|"]
    for r in menu:
        p = r.get("published") or {}
        tk = r.get("ticket") or {}
        L.append("| %.2f | %s | %s | %s | %s | %s | %s |" % (
            r["beta"],
            "-" if r["k"] is None else "%.3f" % r["k"],
            "-" if not tk else "¥%s" % f"{tk['book_amount']:,.0f}",
            "-" if not tk else "¥%s" % f"{tk['cash_amount']:,.0f}",
            "-" if p.get("cagr_pct") is None else "%.2f%%" % p["cagr_pct"],
            "-" if p.get("maxdd_pct") is None else "%.2f%%" % p["maxdd_pct"],
            "-" if p.get("sharpe") is None else "%.2f" % p["sharpe"]))
    if any(r.get("published") is None for r in menu):
        L += ["", "> 注：缺 `results/etf_book_return_regime.json` 的面，回测列留空——不是 0。"]
    if any(r.get("stress") for r in menu):
        L += ["", "## 每档最坏的连续 N 个交易日（现金 0 息，本金全额口径）", "",
              "> 把该档今天的权重原封不动摆回整段面板，取最坏的连续 N 日——不是策略实际路径，",
              "> 是「同一批票、同样的钱」能遇到的最坏窗口。k 只降不升，所以档位越低亏得越少，",
              "> 但不是按比例缩小（窗口是复利口径）。", "",
              "| 目标β | 最坏 1 日 | 最坏 5 日 | 最坏 20 日 |",
              "|---|---|---|---|"]
        for r in menu:
            st = r.get("stress") or {}
            cell = []
            for n in STRESS_WINDOWS:
                w = (st.get("worst") or {}).get("%dd" % n)
                if not w:
                    cell.append("-")
                elif w.get("cny") is None:
                    cell.append("%.2f%%" % w["pct"])
                else:
                    cell.append("%.2f%%（¥%s）" % (w["pct"], f"{w['cny']:,.0f}"))
            L.append("| %.2f | %s | %s | %s |" % (r["beta"], cell[0], cell[1], cell[2]))
        span = next((r["stress"] for r in menu if r.get("stress")), {})
        if span.get("first"):
            L += ["", "口径窗：%s → %s，共 %d 个交易日。"
                  % (span["first"], span["last"], span["n_days"])]
    else:
        L += ["", "> 注：无面板，最坏窗口列不给数——不是「从没亏过」。"]
    for r in menu:
        tk = r.get("ticket")
        L += ["", "## β=%.2f（k=%.3f）" % (r["beta"], r["k"] or 0.0), ""]
        if not tk:
            L += ["- 无票（决策日缺失或该档无历史估计）"]
            continue
        L += ["| 代码 | 权重 | 参考价 | 手数 | 金额 |", "|---|---|---|---|---|"]
        for n in tk["order"]:
            L.append("| %s | %.2f%% | %s | %s | %s |" % (
                n["symbol"], n["weight"] * 100.0,
                "-" if n["price"] is None else "%.4f" % n["price"],
                "-" if n["lots"] is None else str(n["lots"]),
                "-" if n["amount"] is None else "¥%s" % f"{n['amount']:,.0f}"))
        L += ["", "现金腿 %s：¥%s（不足一手零头 ¥%s 未再分配）" % (
            tk["cash_leg"], f"{tk['cash_amount']:,.0f}",
            f"{tk['cash_amount'] - nav * tk['cash_weight']:,.2f}")]
    L += ["", "## 诚实口径", ""]
    L += ["- " + c for c in caveats]
    L += ["- 档位选择是 CEO 的决定；本页只把四档摆在一起，不推荐哪一档。", ""]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------- run
def run(nav=NAV, betas=BETAS):
    mid = machine_id()
    if not writer_allowed(mid):
        print("etf_book_beta_menu: machine=%s is not the writer (%s) -> honest no-op, "
              "nothing written" % (mid, HOST))
        return 0
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    ser, _turnover, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                           O.REBAL, n_hold=O.N_HOLD, cost=F.COST, score=score)
    idx = ser.index.intersection(close[mkt_col].index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(close[mkt_col].reindex(idx))

    grid = [d for d in close.index if d >= pd.Timestamp("2020-01-01")]
    dec_bar = grid[(len(grid) - 1) // O.REBAL * O.REBAL] if grid else None
    asof = str(ser.index[-1].date())

    k_by_beta = {}
    for b in betas:
        sched = O.k_schedule(rp, rm, b)
        k_ser = O.in_force(sched, idx).dropna()
        k_by_beta[b] = None if not len(k_ser) else float(k_ser.iloc[-1])
    cls_map = dict(zip(close.columns, classes))
    menu = ticket_menu(score, close, dec_bar, k_by_beta, nav=nav, classes=cls_map)
    pub = published_tiers()
    for r in menu:
        r["published"] = pub.get(round(r["beta"], 4))
    stress = tier_stress(menu, close, nav, asof) if dec_bar is not None else {}
    for r in menu:
        r["stress"] = stress.get(round(float(r["beta"]), 4))

    caveats = [
        "票池=现存 ETF，存在幸存者偏差",
        "票面按收盘价折算，未计冲击成本与涨跌停",
        "k 每 %d 个交易日重算，段内实际β仍会漂移" % O.REBAL,
        "回测列读自 results/etf_book_return_regime.json（observed 档），非本页现算",
        "最坏窗口=今天权重摆回整段面板的复利最坏 N 日，现金 0 息，非策略实际路径",
        "GC001 单期限滚动假设零费；真实现金台应做期限梯",
    ]
    payload = {"evidence_cutoff": asof,
               "book_decided_at": None if dec_bar is None else str(dec_bar.date()),
               "nav": float(nav), "rebal": O.REBAL, "n_hold": O.N_HOLD,
               "cost_bp_per_side": O.COST_BP, "betas": list(map(float, betas)),
               "menu": menu, "published_source": os.path.relpath(REGIME_JSON, BASE),
               "published_found": bool(pub), "caveats": caveats}

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOC_DIR, exist_ok=True)
    js = os.path.join(OUT_DIR, "MENU-%s.json" % asof)
    with open(js, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    md = os.path.join(DOC_DIR, "TICKET-MENU-%s.md" % asof)
    with open(md, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(menu, asof, None if dec_bar is None else str(dec_bar.date()), nav, caveats))
    with open(os.path.join(OUT_DIR, "latest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"evidence_cutoff": asof, "menu": os.path.relpath(js, BASE),
                   "page": os.path.relpath(md, BASE)}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("menu: %s | decided %s" % (asof, dec_bar))
    for r in menu:
        tk = r["ticket"] or {}
        p = r["published"] or {}
        print("  beta %.2f k=%.3f book=%s cash=%s | published cagr=%s dd=%s"
              % (r["beta"], r["k"] or 0.0,
                 "-" if not tk else "%.0f" % tk["book_amount"],
                 "-" if not tk else "%.0f" % tk["cash_amount"],
                 p.get("cagr_pct"), p.get("maxdd_pct")))
    print("wrote %s" % os.path.relpath(md, BASE))
    return 0


# -------------------------------------------------------------------------- selftest
def selftest():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    ts = pd.Timestamp("2026-10-29")
    # panel fixtures are date-indexed frames row-selected by the decision bar, exactly as
    # the live path does -- a symbol-indexed Series would pass here and crash live.
    px = pd.DataFrame([{"AAA": 10.0, "BBB": 20.0, "CCC": 40.0}], index=[ts])
    sc = pd.DataFrame([{"AAA": 3.0, "BBB": 2.0, "CCC": 1.0}], index=[ts])
    k = {0.10: 0.10, 0.20: 0.20, 0.30: 0.30, 0.50: 1.00}
    menu = ticket_menu(sc, px, ts, k, nav=100_000.0, n_hold=3)

    chk("one row per tier", len(menu) == 4)
    chk("tiers sorted", [r["beta"] for r in menu] == [0.10, 0.20, 0.30, 0.50])
    chk("whole lots", all((n["shares"] or 0) % 100 == 0
                          for r in menu for n in (r["ticket"] or {}).get("order", [])))
    chk("book+cash == nav",
        all(abs((r["ticket"]["book_amount"] + r["ticket"]["cash_amount"]) - 100_000.0) < 0.011
            for r in menu))
    books = [r["ticket"]["book_amount"] for r in menu]
    chk("book monotone in beta", all(b2 >= b1 for b1, b2 in zip(books, books[1:])))
    chk("k=1 cash is lot dust", 0 <= menu[-1]["ticket"]["cash_amount"] < 100 * 40.0)
    names = [[n["symbol"] for n in r["ticket"]["order"]] for r in menu]
    chk("same names across tiers", all(n == names[0] for n in names))

    tmp = os.path.join(OUT_DIR, "_selftest_missing_regime.json")
    chk("absent regime -> {} not zeros", published_tiers(tmp) == {})

    none_menu = ticket_menu(sc, px, None, k, nav=100_000.0, n_hold=3)
    chk("no decision bar -> tickets None",
        len(none_menu) == 4 and all(r["ticket"] is None for r in none_menu))
    unk = ticket_menu(sc, px, ts, {0.20: None}, nav=100_000.0, n_hold=3)
    chk("unknown k -> None ticket", unk[0]["ticket"] is None and unk[0]["k"] is None)

    px2 = pd.Series({"AAA": 10.0, "BBB": float("nan"), "CCC": 40.0})
    sc2 = pd.Series({"AAA": 3.0, "BBB": 2.0, "CCC": 1.0})
    t2 = O.build_ticket(sc2, px2, 0.6, 100_000.0, n_hold=3, lot=100)
    chk("missing price -> None amount",
        any(n["amount"] is None for n in t2["order"])
        and t2["book_amount"] < 100_000.0 * 0.6 + 1e-6)

    md = render(menu, "2026-10-29", "2026-10-29", 100_000.0, ["caveat-A"])
    chk("page has all tiers", all(("β=%.2f" % b) in md for b in k))
    chk("page carries caveats", "caveat-A" in md)

    tmp2 = os.path.join(OUT_DIR, "_selftest_regime.json")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(tmp2, "w", encoding="utf-8") as f:
        json.dump({"cells": [
            {"beta": 0.2, "regime": "observed", "cagr_pct": 9.1, "sharpe": 0.9,
             "maxdd_pct": -12.5},
            {"beta": 0.2, "regime": "zero", "cagr_pct": 99.9, "sharpe": 9.9,
             "maxdd_pct": -0.1}]}, f)
    got2 = published_tiers(tmp2)
    chk("only observed row", got2.get(0.2, {}).get("cagr_pct") == 9.1)
    try:
        os.remove(tmp2)
    except OSError:
        pass

    # 14-18. the worst-window block: deeper at higher k, non-proportional, yuan, absent
    days = pd.date_range("2026-10-01", periods=8, freq="D")
    closes = pd.DataFrame({"AAA": [10.0, 11.0, 9.0, 9.5, 8.0, 8.5, 9.0, 9.2],
                           "BBB": [20.0, 22.0, 18.0, 19.0, 17.0, 18.0, 18.5, 19.0]},
                          index=days)
    scf = pd.DataFrame({"AAA": 3.0, "BBB": 2.0}, index=[days[0]])
    m2 = ticket_menu(scf, closes, days[0], {0.20: 0.20, 1.00: 1.00},
                     nav=100_000.0, n_hold=2)
    sdir = os.path.join(OUT_DIR, "_selftest_stress")
    st2 = tier_stress(m2, closes, 100_000.0, "2026-10-01", cache_dir=sdir, windows=(1, 3))
    lo, hi = st2.get(0.2) or {}, st2.get(1.0) or {}
    chk("L14 stress: both tiers get a worst 1-day", bool((lo.get("worst") or {}).get("1d"))
        and bool((hi.get("worst") or {}).get("1d")))
    if (lo.get("worst") or {}).get("1d") and (hi.get("worst") or {}).get("1d"):
        chk("L15 stress: the fuller book has the deeper 1-day",
            hi["worst"]["1d"]["pct"] < lo["worst"]["1d"]["pct"])
        w = [ (r["ticket"] or {}).get("book_amount", 0.0) / 100_000.0 for r in m2 ]
        ratio = (w[1] / w[0]) if w[0] else None
        naive = lo["worst"]["3d"]["pct"] * ratio if ratio else None
        chk("L16 stress: compounding is not the linear rescale of a smaller tier",
            naive is not None and hi["worst"]["3d"]["pct"] > naive + 1e-9)
        one = hi["worst"]["1d"]
        chk("L17 stress: yuan == pct x capital (to the printed rounding)",
            one.get("cny") is not None and one["cny"] < 0
            and abs(one["cny"] - one["pct"] / 100.0 * 100_000.0) <= 5.0)
    else:
        chk("L16 stress: compounding is not the linear rescale of a smaller tier", False)
        chk("L17 stress: yuan == pct x capital", False)
    none2 = tier_stress(m2, None, 100_000.0, "2026-10-01", cache_dir=sdir)
    chk("L18 stress: absent panel -> None per tier, never 0",
        set(none2) == {0.2, 1.0} and all(v is None for v in none2.values()))
    chk("L19 stress: the cached face replays the same numbers",
        (tier_stress(m2, closes, 100_000.0, "2026-10-01", cache_dir=sdir,
                     windows=(1, 3)).get(1.0) or {}).get("worst")
        == (hi.get("worst")))
    try:
        import shutil
        shutil.rmtree(sdir, ignore_errors=True)
    except OSError:
        pass

    # 20-21. the page tells the reader the risk, and says so when it cannot
    m3 = ticket_menu(scf, closes, days[0], {0.20: 0.20, 1.00: 1.00},
                     nav=100_000.0, n_hold=2)
    st3 = tier_stress(m3, closes, 100_000.0, "2026-10-01",
                      cache_dir=os.path.join(OUT_DIR, "_selftest_stress2"), windows=(1, 3))
    for r in m3:
        r["stress"] = st3.get(round(float(r["beta"]), 4))
    md3 = render(m3, "2026-10-01", "2026-10-01", 100_000.0, ["caveat-A"])
    chk("L20 page carries the worst-window table with money",
        "最坏的连续" in md3 and "¥-" in md3)
    for r in m3:
        r["stress"] = None
    md4 = render(m3, "2026-10-01", "2026-10-01", 100_000.0, ["caveat-A"])
    chk("L21 page says no panel instead of pretending it never lost",
        "无面板" in md4 and "最坏的连续" not in md4)
    try:
        import shutil as _sh
        _sh.rmtree(os.path.join(OUT_DIR, "_selftest_stress2"), ignore_errors=True)
    except OSError:
        pass

    total = 21
    if fails:
        print("etf_book_beta_menu selftest FAIL %d/%d: %s" % (len(fails), total, ", ".join(fails)))
        return 1
    print("etf_book_beta_menu selftest %d/%d PASS" % (total, total))
    return 0


def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    nav = NAV
    for a in args:
        if a.startswith("--nav="):
            nav = float(a.split("=", 1)[1])
    return run(nav=nav, betas=BETAS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))