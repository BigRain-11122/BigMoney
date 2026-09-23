"""Portfolio simulator with A-share rules.

Execution model (no lookahead):
  - signals computed at day T close (family masks over the signal window)
  - buys execute at day T+1 open (skipped if opening at limit-up / suspended)
  - sells execute at day T+1 open (deferred while opening at limit-down)
  - T+1 rule is structurally satisfied: earliest sell is the day after entry
  - fees: commission 0.025% (min ¥5) both sides + stamp tax 0.05% on sells
  - slippage 0.1% per side; order capped at 5% of the day's turnover; lots of 100
"""
import numpy as np

import config as C

FAM_EXIT_MA = ("breakout", "pullback", "smallmom",  # exit when close < MA20
               "vcp", "gapup", "streak", "newhigh250", "macd",
               "lowvol", "turnspike", "atrbreak", "adxstrong", "momspeed",
               "lotterylow", "intraday", "illiq", "confluence", "lhb")
FAM_EXIT_MA10 = ("meanrev", "bollrev", "crashst", "diplimit",  # close > MA10
                 "kdjgold", "ccirev", "wrrev", "mfidip", "engulf")


def simulate(A_exec, fams, gp, regime, i0):
    """A_exec: execution-window arrays (row k = absolute day i0 + k).
    fams: {fam: (mask, score)} aligned so row j = signal day (i0 - 1 + j).
    gp: decoded genome params (K/stop/trail/hold/exposure/w). regime: [T] ids.
    Returns dict(eq, invested, trades, metrics)."""
    W = int(A_exec["close"].shape[0])
    fam_names = sorted(fams.keys())
    masks = np.stack([np.asarray(fams[f][0]) for f in fam_names])   # [F, W, N]
    scores = np.stack([np.asarray(fams[f][1]) for f in fam_names]).astype(np.float32)
    open_ = A_exec["open"]; close_ = A_exec["close"]; amount_ = A_exec["amount"]
    ban = A_exec["open_ban"]; bust = A_exec["open_bust"]
    ma10 = A_exec["ma10"]; ma20 = A_exec["ma20"]; pc = A_exec["pct_chg"]

    K = int(gp["K"]); stop = gp["stop"]; trail = gp["trail"]; hold = int(gp["hold"])
    expo = gp["exposure"]; Wgt = gp["w"]

    cash = C.CAPITAL
    pos = {}
    eq = np.empty(W, dtype=np.float64)
    inv = np.empty(W, dtype=np.float64)
    trades = []
    buy_total = 0.0

    for k in range(W):
        o = open_[k]
        c = close_[k]
        # ---- sells at open
        for i in list(pos.keys()):
            p = pos[i]
            if not (p["sell"] or p["pend"]):
                continue
            oi = o[i]
            if not np.isfinite(oi) or bust[k, i]:
                p["pend"] = True
                continue
            px = float(oi) * (1 - C.SLIPPAGE)
            gross = p["shares"] * px
            fee = max(C.COMMISSION * gross, C.MIN_COMMISSION) + C.STAMP_TAX * gross
            cash += gross - fee
            pnl = gross - fee - p["cash_cost"]
            trades.append({"i": int(i), "entry_day": p["entry_day"], "exit_day": k,
                           "ret": pnl / p["cash_cost"], "hold": k - p["bday"],
                           "fam": p["fam"], "reason": p["reason"],
                           "cost": p["cash_cost"], "gross": gross})
            del pos[i]
        # ---- buys at open (signals from the previous day's close = T+1;
        # alignment fixed 2026-09-21: fams row k = signal day i0-1+k, so
        # buying at day k uses the day-before close, not two days before)
        j = k
        cand = masks[:, j, :].any(axis=0)
        if cand.any():
            r = int(regime[i0 - 1 + j])
            w = Wgt[r]
            blended = (scores[:, j, :] * w[:, None]).sum(axis=0)
            cand_idx = np.where(cand)[0]
            order = cand_idx[np.argsort(-blended[cand_idx])]
            eqv = cash + sum(p["shares"] * p["last"] for p in pos.values())
            per = min(eqv * expo[r] / K, eqv * C.MAX_POS_PCT)
            for i in order[: K * 3]:
                if len(pos) >= K or per <= 0:
                    break
                if int(i) in pos:
                    continue
                oi = o[i]
                if not np.isfinite(oi) or ban[k, i]:
                    continue
                px = float(oi) * (1 + C.SLIPPAGE)
                shares = int(per / px / C.LOT) * C.LOT
                if shares < C.LOT:
                    continue
                capv = C.AMOUNT_PART_CAP * float(amount_[k, i])
                if not np.isfinite(capv) or capv <= 0:
                    continue
                if shares * px > capv:
                    shares = int(capv / px / C.LOT) * C.LOT
                    if shares < C.LOT:
                        continue
                cost = shares * px
                fee = max(C.COMMISSION * cost, C.MIN_COMMISSION)
                if cost + fee > cash:
                    shares = int(cash * 0.999 / (px * (1 + C.COMMISSION)) / C.LOT) * C.LOT
                    if shares < C.LOT:
                        continue
                    cost = shares * px
                    fee = max(C.COMMISSION * cost, C.MIN_COMMISSION)
                    if cost + fee > cash:
                        continue
                cash -= cost + fee
                buy_total += cost + fee
                fam_row = masks[:, j, i]
                ws = np.where(fam_row, w * scores[:, j, i], -1.0)
                fidx = int(np.argmax(ws))
                ci = c[i]
                pos[int(i)] = dict(shares=shares, cost=px, cash_cost=cost + fee,
                                   peak=px, bday=k, entry_day=k,
                                       last=float(ci) if np.isfinite(ci) else px,
                                       fam=fam_names[fidx], pend=False, sell=False,
                                       reason="")
        # ---- mark to close & generate next-day sell signals
        invested = 0.0
        for i, p in pos.items():
            ci = c[i]
            if np.isfinite(ci):
                p["last"] = float(ci)
                p["peak"] = max(p["peak"], p["last"])
            invested += p["shares"] * p["last"]
        eq[k] = cash + invested
        inv[k] = invested
        for i, p in pos.items():
            ci = c[i]
            if not np.isfinite(ci):
                continue
            cif = float(ci)
            reason = ""
            if cif <= p["cost"] * (1 - stop):
                reason = "stop"    # protective stop: usable from day 0
            elif k - p["bday"] + 1 >= C.MIN_HOLD_DAYS:
                # min-hold gate (user rule 2026-09-22): trail/signal/time
                # exits only after >=3 completed sessions
                if cif <= p["peak"] * (1 - trail):
                    reason = "trail"
                else:
                    f = p["fam"]
                    if f in FAM_EXIT_MA and cif < float(ma20[k, i]):
                        reason = "signal"
                    elif f == "limitup" and float(pc[k, i]) < 0:
                        reason = "signal"
                    elif f in FAM_EXIT_MA10 and cif > float(ma10[k, i]):
                        reason = "signal"
                if not reason and k - p["bday"] >= hold:
                    reason = "time"
            if reason:
                p["sell"] = True
                p["reason"] = reason

    m = metrics(eq, inv, trades, buy_total, W)
    return {"eq": eq, "invested": inv, "trades": trades, "metrics": m}


def metrics(eq, inv, trades, buy_total, W):
    ret = eq[1:] / eq[:-1] - 1 if W > 1 else np.array([])
    n = len(ret)
    years = W / 252.0
    total = float(eq[-1] / eq[0] - 1) if W else 0.0
    cagr = float((eq[-1] / eq[0]) ** (1 / years) - 1) if years > 0 and eq[-1] > 0 else 0.0
    sd = float(ret.std()) if n else 0.0
    sharpe = float(ret.mean() / (sd + 1e-12) * np.sqrt(252)) if n else 0.0
    peak = np.maximum.accumulate(eq) if W else eq
    dd = eq / peak - 1 if W else np.array([0.0])
    maxdd = float(dd.min()) if W else 0.0
    win = sum(1 for t in trades if t["ret"] > 0)
    m = {
        "total": total, "cagr": cagr, "vol": sd * np.sqrt(252), "sharpe": sharpe,
        "maxdd": maxdd, "calmar": (cagr / abs(maxdd)) if maxdd < -1e-9 else 0.0,
        "n_trades": len(trades), "win_rate": (win / len(trades)) if trades else 0.0,
        "avg_hold": float(np.mean([t["hold"] for t in trades])) if trades else 0.0,
        "turnover_ann": float(buy_total / max(eq.mean(), 1.0) / max(years, 1e-9)),
        "exposure": float(inv.mean() / max(eq.mean(), 1e-9)),
    }
    return m


def fitness(m):
    f = m["sharpe"] - 0.10 * m["turnover_ann"]
    f -= 2.0 * max(0.0, m["maxdd"] + 0.28)
    if m["n_trades"] < 20:
        f -= (20 - m["n_trades"]) * 0.05
    return f
