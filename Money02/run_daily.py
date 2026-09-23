"""Daily auto-iteration: data update -> cache rebuild -> paper execution ->
walk-forward evolution -> report + next-day signals -> history log.

Paper book (100万虚拟本金): applies the PREVIOUS run's signal file at the new
trade day's actual opens (limit-up blocks buys / limit-down defers sells),
marks at close, then the freshly evolved genome issues tomorrow's orders.
"""
import json
import os
import time
import datetime as dt

import numpy as np

import config as C
import data as D
import evolve as EV
import report as RP
import backtest as BT


def load_paper():
    p = RP.paper_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"cash": C.CAPITAL, "positions": {}, "history": [], "last_exec_date": ""}


def save_paper(paper):
    RP.paper_path().write_text(json.dumps(paper, ensure_ascii=False, indent=2),
                               encoding="utf-8")


def paper_step(cache, sig):
    """Execute yesterday's signals at the last cached trade day's open; mark to
    close; refresh sell flags with the managing genome's exit rules."""
    paper = load_paper()
    T = int(len(cache["dates"]))
    ex = T - 1
    date_s = str(np.asarray(cache["dates"])[ex])
    if paper.get("last_exec_date") == date_s:
        return paper  # already executed for this trade day (idempotent)
    codes = {str(c): i for i, c in enumerate(np.asarray(cache["codes"]))}
    o = np.asarray(cache["open"][ex]); c = np.asarray(cache["close"][ex])
    ban = np.asarray(cache["open_ban"][ex]); bust = np.asarray(cache["open_bust"][ex])
    amt = np.asarray(cache["amount"][ex])
    ma10 = np.asarray(cache["ma10"][ex]); ma20 = np.asarray(cache["ma20"][ex])
    pc = np.asarray(cache["pct_chg"][ex])

    # ---- sells at open (flags from previous close, or pending retries)
    for code in list(paper["positions"].keys()):
        p = paper["positions"][code]
        if not (p.get("sell") or p.get("pend")):
            continue
        i = codes.get(code)
        if i is None or not np.isfinite(o[i]) or bust[i]:
            p["pend"] = True
            continue
        px = float(o[i]) * (1 - C.SLIPPAGE)
        gross = p["shares"] * px
        fee = max(C.COMMISSION * gross, C.MIN_COMMISSION) + C.STAMP_TAX * gross
        paper["cash"] += gross - fee
        paper.setdefault("closed", []).append(
            {"code": code, "date": date_s, "px": round(px, 3),
             "ret": round((gross - fee) / p["cash_cost"] - 1, 4),
             "hold_days": p.get("hold_days", 0), "reason": p.get("reason", "")})
        del paper["positions"][code]

    # ---- buys at open
    K = int(sig.get("K", 6))
    expo = float(sig.get("exposure", 0.8))
    eq_now = paper["cash"] + sum(p["shares"] * p.get("last", p["cost"])
                                 for p in paper["positions"].values())
    per = min(eq_now * expo / max(K, 1), eq_now * C.MAX_POS_PCT)
    for b in sig.get("buys", []):
        if len(paper["positions"]) >= K or per <= 0:
            break
        code = b["code"]
        if code in paper["positions"]:
            continue
        i = codes.get(code)
        if i is None or not np.isfinite(o[i]) or ban[i]:
            continue
        px = float(o[i]) * (1 + C.SLIPPAGE)
        shares = int(per / px / C.LOT) * C.LOT
        if shares < C.LOT:
            continue
        capv = C.AMOUNT_PART_CAP * float(amt[i])
        if not np.isfinite(capv) or capv <= 0:
            continue
        if shares * px > capv:
            shares = int(capv / px / C.LOT) * C.LOT
            if shares < C.LOT:
                continue
        cost = shares * px
        fee = max(C.COMMISSION * cost, C.MIN_COMMISSION)
        if cost + fee > paper["cash"]:
            continue
        paper["cash"] -= cost + fee
        paper["positions"][code] = {
            "shares": shares, "cost": px, "cash_cost": cost + fee, "peak": px,
            "bday_date": date_s, "hold_days": 0,
            "last": float(c[i]) if np.isfinite(c[i]) else px,
            "fam": b.get("fam", ""), "pend": False, "sell": False, "reason": "",
        }

    # ---- mark to close, refresh exit flags for tomorrow
    stop = float(sig.get("stop") or 0.08)
    trail = float(sig.get("trail") or 0.10)
    hold = int(sig.get("hold") or 5)
    for code, p in paper["positions"].items():
        i = codes.get(code)
        if i is None:
            continue
        p["hold_days"] = p.get("hold_days", 0) + 1
        ci = c[i]
        if not np.isfinite(ci):
            continue
        p["last"] = float(ci)
        p["peak"] = max(p["peak"], p["last"])
        cif = p["last"]
        reason = ""
        if cif <= p["cost"] * (1 - stop):
            reason = "stop"    # protective stop: usable from day 0
        elif p["hold_days"] >= C.MIN_HOLD_DAYS:
            # min-hold gate (user rule 2026-09-22): trail/signal/time
            # exits only after >=3 completed sessions
            if cif <= p["peak"] * (1 - trail):
                reason = "trail"
            else:
                f = p.get("fam", "")
                if f in BT.FAM_EXIT_MA and cif < float(ma20[i]):
                    reason = "signal"
                elif f == "limitup" and float(pc[i]) < 0:
                    reason = "signal"
                elif f == "meanrev" and cif > float(ma10[i]):
                    reason = "signal"
            if not reason and p["hold_days"] >= hold:
                reason = "time"
        p["sell"] = bool(reason)
        p["reason"] = reason
        p["pend"] = False

    equity = paper["cash"] + sum(p["shares"] * p.get("last", p["cost"])
                                 for p in paper["positions"].values())
    paper["history"].append({"date": date_s, "equity": round(equity, 2),
                             "cash": round(paper["cash"], 2),
                             "n_pos": len(paper["positions"])})
    paper["last_exec_date"] = date_s
    save_paper(paper)
    print(f"paper[{date_s}]: equity={equity:,.0f} positions={len(paper['positions'])} "
          f"cash={paper['cash']:,.0f}")
    return paper


def _full_run_alive_young():
    """True if a healthy full cycle is already running (防双跑: tick-launched
    run + scheduled MoneyQuantDaily must never stack two multi-hour WF runs)."""
    p = C.RESULTS_DIR / "full_run.pid"
    if not p.exists():
        return False
    try:
        pid = int(p.read_text().strip() or 0)
        age = time.time() - p.stat().st_mtime
    except Exception:  # noqa: BLE001
        return False
    alive = False
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if h:
            k.CloseHandle(h)
            alive = True
    except Exception:  # noqa: BLE001
        pass
    if pid and alive:
        return age <= 360 * 60  # a true hang is left to tick police
    try:
        p.unlink()
    except OSError:
        pass
    return False


def main():
    if _full_run_alive_young():
        print("full cycle already in progress - exit (single-flight)")
        return
    t0 = time.time()
    print(f"=== run_daily {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    fullpid = C.RESULTS_DIR / "full_run.pid"
    fullpid.write_text(str(os.getpid()))  # self-register for tick police
    try:
        _main_inner(t0)
    finally:
        fullpid.unlink(missing_ok=True)


def _main_inner(t0):
    state_p = C.RESULTS_DIR / "state.json"
    state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}
    D.update_index()
    ltd = D.last_trade_date()
    if ltd is None:
        print("no index data; run a full download first")
        return
    if state.get("last_trade_date") == str(ltd):
        print(f"no new trade data since {ltd}; done ({time.time() - t0:.0f}s)")
        return
    D.update_data()
    D.build_cache()

    # 1) paper execution of yesterday's signals at today's open (BEFORE new signals)
    cache = D.load_cache(mmap=False)
    if RP.signals_path().exists():
        old_sig = json.loads(RP.signals_path().read_text(encoding="utf-8"))
        paper = paper_step(cache, old_sig)
    else:
        paper = load_paper()

    # 2) evolution + report + new signals
    tag = str(ltd)[:10].replace("-", "")
    res = EV.run_walkforward(tag=tag)
    m = RP.make_report(res)
    RP.write_signals(res["cache"], res["live"], res["regime"], res["out_dir"])

    # champion certification battery (六道出厂门禁) - non-fatal
    try:
        import certify
        certify.main()
    except Exception as e:  # noqa: BLE001
        print(f"certify failed (non-fatal): {e}")

    equity = paper["cash"] + sum(p["shares"] * p.get("last", p["cost"])
                                 for p in paper["positions"].values())
    hist = {"date": str(ltd)[:10], "oos_total": round(m["total"], 4),
            "oos_cagr": round(m["cagr"], 4), "oos_sharpe": round(m["sharpe"], 3),
            "oos_maxdd": round(m["maxdd"], 4), "n_folds": res["summary"]["n_folds"],
            "paper_equity": round(equity, 0), "elapsed_s": round(time.time() - t0, 1)}
    with open(C.RESULTS_DIR / "history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(hist, ensure_ascii=False) + "\n")
    state["last_trade_date"] = str(ltd)
    state["last_tag"] = tag
    state_p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"=== done in {time.time() - t0:.0f}s | OOS total={m['total'] * 100:.1f}% "
          f"sharpe={m['sharpe']:.2f} paper={equity:,.0f} ===")


if __name__ == "__main__":
    main()
