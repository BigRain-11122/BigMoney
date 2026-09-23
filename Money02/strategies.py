"""Strategy gene families: parameterized short-term A-share entry logic.

Each family produces (entry_mask, score) over a *signal window* slice of the
panel. Convention: caller passes the signal window whose row j corresponds
to the day BEFORE execution day j of the execution window (next-open
execution), so all information used here is known at signal close time. No
lookahead.

30 families (user orders: 实战海选/极度细分流派/交叉融合):
  breakout  放量新高突破   limitup   首板次日接力   meanrev  超跌企稳反弹
  pullback  强趋势缩量回调 smallmom 小盘动量       relstr   RPS相对强度
  nrev      N字反包        volburst 量价起爆
  vcp       平台缩量突破   gapup    缺口跳空延续   streak   连阳动量
  newhigh250 年线新高      macd     水上金叉       lowvol   低波防御动量
  turnspike 换手异动       bollrev  布林下轨反转   crashst  急跌企稳首阳
  diplimit  开板反包
  kdjgold   随机低位金叉   ccirev   CCI超卖回升   wrrev    威廉超卖
  mfidip    资金流超卖     atrbreak 波动扩张突破   adxstrong 强趋势延续
  momspeed  动量加速       lotterylow 低彩票稳态动量 illiq   非流动异象
  intraday  日内强隔夜弱   engulf   阳包阴形态     confluence 多流派共振

Selectivity (2026-09-21): family_signals(A, params, fams=None) computes ONLY
the requested families - the hot eval path passes the genome's weighted
families so a 30-family space costs like an 8-family one. One-shot callers
(report/certify/signals) pass fams=None for the full set. Field-gated
families sleep as zero-masks until their panel fields exist, so code deploys
BEFORE the cache rebuild without KeyError loops.
"""
import numpy as np

FAMILIES = ["breakout", "limitup", "meanrev", "pullback", "smallmom",
            "relstr", "nrev", "volburst",
            "vcp", "gapup", "streak", "newhigh250", "macd", "lowvol",
            "turnspike", "bollrev", "crashst", "diplimit",
            "kdjgold", "ccirev", "wrrev", "mfidip", "atrbreak", "adxstrong",
            "momspeed", "lotterylow", "illiq", "intraday", "engulf",
            "confluence", "lhb"]

# (param, kind, args); kind: f=float linear, int=integer, pick=options
SCHEMA = {
    "breakout": [("lb", "pick", [20, 60]),
                 ("volx", "f", [1.2, 4.0]),
                 ("ma_sel", "pick", [10, 20, 60]),
                 ("mom_min", "f", [0.0, 0.15])],
    "limitup": [("quiet", "int", [2, 6]),
                ("amt_hi", "f", [0.85, 0.995])],
    "meanrev": [("mom_thr", "f", [-0.30, -0.05]),
                ("rsi_hi", "f", [15.0, 40.0]),
                ("stab", "f", [0.2, 0.7])],
    "pullback": [("slope_min", "f", [0.0, 0.05]),
                 ("vrx", "f", [0.4, 1.3]),
                 ("deep", "f", [0.0, 0.03])],
    "smallmom": [("mom_min", "f", [0.05, 0.30]),
                 ("size_thr", "f", [0.15, 0.7])],
    "relstr": [("rps_hi", "f", [0.80, 0.97]),
               ("rps_lo", "f", [0.50, 0.95]),
               ("volx", "f", [1.0, 2.5])],
    "nrev": [("drop", "f", [2.0, 8.0]),
             ("volx", "f", [1.2, 3.0])],
    "volburst": [("quiet", "f", [0.005, 0.06]),
                 ("volx", "f", [1.8, 5.0])],
    "vcp": [("rng_max", "f", [0.02, 0.30]),
            ("vrx", "f", [0.3, 1.5])],
    "gapup": [("gap_min", "f", [0.5, 5.0]),
              ("gap_max", "f", [3.0, 9.0]),
              ("mom_min", "f", [0.0, 0.10])],
    "streak": [("days", "int", [2, 5]),
               ("thr", "f", [0.0, 2.0])],
    "newhigh250": [("volx", "f", [0.8, 4.0])],
    "macd": [],
    "lowvol": [("rng_max", "f", [0.02, 0.20]),
               ("mom_min", "f", [0.0, 0.20])],
    "turnspike": [("vr_min", "f", [1.5, 6.0]),
                  ("up_min", "f", [1.0, 6.0])],
    "bollrev": [("nsd", "f", [1.5, 3.0]),
                ("rsi_hi", "f", [20.0, 40.0])],
    "crashst": [("dd_min", "f", [0.10, 0.35]),
                ("up_min", "f", [1.0, 5.0]),
                ("vr_hi", "f", [0.6, 1.5])],
    "diplimit": [("rec_min", "f", [3.0, 9.0])],
    "kdjgold": [("k_hi", "f", [20.0, 45.0])],
    "ccirev": [("cci_lo", "f", [-250.0, -80.0])],
    "wrrev": [("wr_lo", "f", [-98.0, -70.0])],
    "mfidip": [("mfi_lo", "f", [5.0, 25.0])],
    "atrbreak": [("atr_mult", "f", [1.2, 3.0])],
    "adxstrong": [("adx_min", "f", [18.0, 40.0])],
    "momspeed": [("accel_min", "f", [0.0, 0.10])],
    "lotterylow": [("max_hi", "f", [0.02, 0.09])],
    "illiq": [("mom_min", "f", [0.05, 0.30]),
              ("rk_lo", "f", [0.55, 0.95])],
    "intraday": [("in_min", "f", [0.5, 5.0]),
                 ("gap_max", "f", [-3.0, 1.0])],
    "engulf": [("pen", "f", [0.0, 3.0])],
    "confluence": [("need", "int", [2, 3])],
    "lhb": [("nb_min", "f", [0.5, 20.0])],
}


def _sh(a, n=1):
    out = np.zeros_like(a)
    if a.shape[0] > n:
        out[n:] = a[:-n]
    return out


def family_signals(A, params, fams=None):
    """A: signal-window arrays; params: {fam: {param: value}}.
    fams: iterable of family names to compute (None = all). Returns
    {fam: (mask[TW,N], score[TW,N])}, score 0 where mask is False. Families
    whose panel fields are absent sleep as zero-masks."""
    close = np.asarray(A["close"]); ma10 = np.asarray(A["ma10"])
    ma20 = np.asarray(A["ma20"]); ma60 = np.asarray(A["ma60"])
    mom20 = np.asarray(A["mom20"]); vr = np.asarray(A["vol_ratio5"])
    rsi = np.asarray(A["rsi14"]); rh20 = np.asarray(A["roll_high20"])
    rh60 = np.asarray(A["roll_high60"]); rng = np.asarray(A["rng_pos"])
    slope = np.asarray(A["ma20_slope"]); rank = np.asarray(A["amt_rank"])
    cap_rank = np.asarray(A["mktcap_rank"])
    pc = np.asarray(A["pct_chg"]); lu = np.asarray(A["limit_up"])
    tr = np.asarray(A["tradable"]); op = np.asarray(A["open"])
    rps50 = np.asarray(A["rps50"]); rps120 = np.asarray(A["rps120"])
    mom50 = np.asarray(A["mom50"])
    out = {}
    want = set(fams) if fams is not None else None

    def go(nm):
        return want is None or nm in want

    def sleep(nm):
        out[nm] = (np.zeros(pc.shape, dtype=bool),
                   np.zeros(pc.shape, np.float32))

    if go("breakout"):
        p = params["breakout"]
        rh = rh20 if p["lb"] == 20 else rh60
        ma = {10: ma10, 20: ma20, 60: ma60}[p["ma_sel"]]
        m = ((close > _sh(rh)) & (vr >= p["volx"]) & (close > ma)
             & (mom20 >= p["mom_min"]) & tr)
        s = np.clip(mom20, 0, 0.4) + 0.02 * np.minimum(vr, 8.0)
        out["breakout"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("limitup"):
        p = params["limitup"]
        prior = np.zeros(lu.shape, dtype=bool)
        for i in range(1, p["quiet"] + 1):
            prior |= _sh(lu, i)
        m = lu & ~prior & (rank <= p["amt_hi"]) & tr
        s = np.nan_to_num(rank) * 0.8 + np.clip(mom20, 0, 0.5) * 0.4
        out["limitup"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("meanrev"):
        p = params["meanrev"]
        m = ((mom20 <= p["mom_thr"]) & (rsi <= p["rsi_hi"])
             & (rng >= p["stab"]) & (close > op) & tr)
        s = -mom20 + np.nan_to_num(rng) * 0.1
        out["meanrev"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("pullback"):
        p = params["pullback"]
        near = close / np.where(ma10 != 0, ma10, np.nan) - 1.0
        m = ((close > ma20) & (slope >= p["slope_min"]) & (vr <= p["vrx"])
             & (near <= p["deep"]) & tr)
        s = np.clip(np.nan_to_num(slope) * 20.0, 0, 1.0) + np.nan_to_num(rng) * 0.3
        out["pullback"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("smallmom"):
        p = params["smallmom"]
        m = ((mom20 >= p["mom_min"]) & (cap_rank <= p["size_thr"]) & (close > ma20) & tr)
        s = np.clip(mom20, 0, 0.5) * 2.0 + (1.0 - np.nan_to_num(cap_rank)) * 0.3
        out["smallmom"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("relstr"):
        p = params["relstr"]
        m = ((rps50 >= p["rps_hi"]) & (rps120 >= p["rps_lo"])
             & (close > ma20) & (vr >= p["volx"]) & (rng >= 0.4) & tr)
        s = np.nan_to_num(rps50) * 1.5 + np.nan_to_num(rps120) * 0.5
        out["relstr"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("nrev"):
        p = params["nrev"]
        prev_pc = _sh(pc)
        engul = (close > op) & (close >= _sh(np.where(op > 0, op, np.nan)))
        m = ((prev_pc <= -p["drop"]) & engul & (vr >= p["volx"]) & (rng >= 0.5) & tr)
        s = -np.nan_to_num(prev_pc) * 0.3 + np.clip(mom20, 0, 0.3)
        out["nrev"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("volburst"):
        p = params["volburst"]
        quiet = np.abs(mom20) <= p["quiet"]
        m = (quiet & (vr >= p["volx"]) & (close > op) & (close > ma20) & tr)
        s = np.minimum(np.nan_to_num(vr), 8.0) * 0.1 + np.nan_to_num(rng) * 0.5
        out["volburst"] = (m, np.where(m, s, 0.0).astype(np.float32))

    gap = np.asarray(A["gap"]); dd60 = np.asarray(A["dd60"]) \
        if go("crashst") or go("gapup") else None
    dif = np.asarray(A["macd_dif"]) if ("macd_dif" in A and
                                        (go("macd") or go("confluence"))) else None
    dea = np.asarray(A["macd_dea"]) if dif is not None else None
    rh250 = np.asarray(A["rh250"]) if ("rh250" in A and go("newhigh250")) else None
    up_ok = np.isfinite(pc) & (pc > 0)

    if go("vcp"):
        p = params["vcp"]
        m = ((rng <= p["rng_max"]) & (vr <= p["vrx"]) & (close > _sh(rh20)) & tr)
        s = (1.0 - np.nan_to_num(rng)) + 0.02 * np.minimum(np.nan_to_num(vr), 4.0)
        out["vcp"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("gapup"):
        p = params["gapup"]
        m = ((gap >= p["gap_min"]) & (gap <= p["gap_max"]) & (close > op)
             & (mom20 >= p["mom_min"]) & (close > ma20) & tr)
        s = np.clip(np.nan_to_num(gap) * 0.3, 0, 2.0) + np.clip(mom20, 0, 0.3)
        out["gapup"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("streak"):
        p = params["streak"]
        cs_up = np.cumsum(up_ok.astype(np.int32), axis=0)
        base = np.maximum.accumulate(np.where(~up_ok, cs_up, 0), axis=0)
        run = np.where(up_ok, cs_up - base, 0).astype(np.int16)
        m = ((run >= p["days"]) & (pc >= p["thr"] * 0.01 - 1e-9) & (close > ma20) & tr)
        s = np.clip(run.astype(np.float32), 0, 6) * 0.15 + np.clip(mom20, 0, 0.4)
        out["streak"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("newhigh250"):
        p = params["newhigh250"]
        if rh250 is not None:
            m = ((close >= _sh(rh250) * 0.999) & (vr >= p["volx"])
                 & (close > ma20) & tr)
            s = np.clip(mom50, 0, 0.6) + np.nan_to_num(rps120) * 0.5
            out["newhigh250"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("newhigh250")

    if go("macd"):
        if dif is not None:
            cross = (dif > dea) & (_sh(dif) <= _sh(dea)) & (dif > 0) & (dea > 0)
            m = (cross & (close > ma20) & tr)
            s = np.clip(np.nan_to_num(dif), 0, 2.0) + np.clip(mom20, 0, 0.3)
            out["macd"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("macd")

    if go("lowvol"):
        p = params["lowvol"]
        m = ((rng <= p["rng_max"]) & (mom20 >= p["mom_min"]) & (close > ma20)
             & (ma20 > ma60) & tr)
        s = (1.0 - np.nan_to_num(rng)) + np.clip(mom20, 0, 0.3) * 0.5
        out["lowvol"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("turnspike"):
        p = params["turnspike"]
        m = ((vr >= p["vr_min"]) & (pc >= p["up_min"] * 0.01 - 1e-9)
             & (close > op) & (rank <= 0.5) & tr)
        s = np.minimum(np.nan_to_num(vr), 10.0) * 0.15 + np.clip(pc, 0, 0.1) * 3.0
        out["turnspike"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("bollrev"):
        p = params["bollrev"]
        cl = close
        ok = np.isfinite(cl)
        cs = np.cumsum(np.where(ok, cl, 0.0), axis=0)
        cs2 = np.cumsum(np.where(ok, cl, 0.0) ** 2, axis=0)
        cn = np.cumsum(ok.astype(np.float32), axis=0)
        k = 20
        ma_b = np.full_like(cl, np.nan)
        sd_b = np.full_like(cl, np.nan)
        if cl.shape[0] > k:
            S = cs[k:] - cs[:-k]
            C2 = cs2[k:] - cs2[:-k]
            V = cn[k:] - cn[:-k]
            valid = V >= k - 0.5
            m1 = S / k
            v = C2 / k - m1 * m1
            okv = valid & (v > 0)
            ma_b[k:] = np.where(okv, m1, np.nan)
            sd_b[k:] = np.where(okv, np.sqrt(np.maximum(v, 0.0)), np.nan)
        low_band = ma_b - p["nsd"] * sd_b
        m = (np.isfinite(low_band) & (close <= low_band) & (rsi <= p["rsi_hi"]) & tr)
        s = (p["rsi_hi"] - np.nan_to_num(rsi)) * 0.05 + np.clip(-mom20, 0, 0.3)
        out["bollrev"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("crashst"):
        p = params["crashst"]
        m = ((dd60 <= -p["dd_min"]) & (vr <= p["vr_hi"])
             & (pc >= p["up_min"] * 0.01 - 1e-9) & (close > op)
             & (_sh(pc) < 0) & tr)
        s = np.clip(-np.nan_to_num(dd60), 0, 0.5) + np.clip(pc, 0, 0.08) * 5.0
        out["crashst"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("diplimit"):
        p = params["diplimit"]
        bust = np.asarray(A["open_bust"])
        recov = np.where(op > 0, close / op - 1.0, np.nan)
        m = (bust & (recov >= p["rec_min"] * 0.01 - 1e-9) & (close > op) & tr)
        s = np.clip(np.nan_to_num(recov), 0, 0.2) * 10.0 + np.clip(pc, 0, 0.1) * 5.0
        out["diplimit"] = (m, np.where(m, s, 0.0).astype(np.float32))

    # ---- 12 细分/融合家族 ----
    def has(*fs):
        return all(f in A for f in fs)

    if go("kdjgold"):
        if has("stoch_k", "stoch_d"):
            p = params["kdjgold"]
            sk = np.asarray(A["stoch_k"]); sd = np.asarray(A["stoch_d"])
            m = ((sk > sd) & (_sh(sk) <= _sh(sd)) & (sk <= p["k_hi"])
                 & (sk > 10) & (close > op) & tr)
            s = np.clip(np.nan_to_num(sd), 0, 50) * 0.02 + np.clip(pc, 0, 0.08) * 4.0
            out["kdjgold"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("kdjgold")

    if go("ccirev"):
        if has("cci14"):
            p = params["ccirev"]
            cci = np.asarray(A["cci14"])
            m = ((_sh(cci) <= p["cci_lo"]) & (cci > p["cci_lo"])
                 & (cci < -30) & (close > op) & tr)
            s = np.clip(p["cci_lo"] - np.nan_to_num(cci), 0, 150) * 0.02
            out["ccirev"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("ccirev")

    if go("wrrev"):
        if has("wr10"):
            p = params["wrrev"]
            wr = np.asarray(A["wr10"])
            m = ((wr <= p["wr_lo"]) & (close > op) & (rng >= 0.5) & tr)
            s = (np.nan_to_num(wr) + 100.0) * 0.05 + np.nan_to_num(rng) * 0.3
            out["wrrev"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("wrrev")

    if go("mfidip"):
        if has("mfi14"):
            p = params["mfidip"]
            mfi = np.asarray(A["mfi14"])
            m = ((mfi <= p["mfi_lo"]) & (close > op) & (rng >= 0.5) & tr)
            s = (p["mfi_lo"] - np.nan_to_num(mfi)) * 0.1 + np.nan_to_num(rng) * 0.4
            out["mfidip"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("mfidip")

    if go("atrbreak"):
        if has("atr14"):
            p = params["atrbreak"]
            atr = np.asarray(A["atr14"])
            approx = (np.abs(close - op) + np.abs(close - _sh(close))) \
                / np.maximum(atr, 1e-9)
            m = ((approx >= p["atr_mult"]) & (close > op) & (close > ma20)
                 & (mom20 > 0) & tr)
            s = np.clip(approx, 0, 5) * 0.2 + np.clip(mom20, 0, 0.3)
            out["atrbreak"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("atrbreak")

    if go("adxstrong"):
        if has("adx14"):
            p = params["adxstrong"]
            adx = np.asarray(A["adx14"])
            m = ((adx >= p["adx_min"]) & (close > ma20) & (mom20 > 0.03)
                 & (slope > 0) & tr)
            s = np.clip(np.nan_to_num(adx), 0, 60) * 0.03 + np.clip(mom20, 0, 0.3)
            out["adxstrong"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("adxstrong")

    if go("momspeed"):
        if has("mom_accel"):
            p = params["momspeed"]
            acc = np.asarray(A["mom_accel"])
            m = ((acc >= p["accel_min"]) & (mom20 > 0) & (close > ma20)
                 & (vr >= 1.0) & tr)
            s = np.clip(np.nan_to_num(acc), 0, 0.3) * 2.0 + np.clip(mom20, 0, 0.4)
            out["momspeed"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("momspeed")

    if go("lotterylow"):
        if has("maxret20"):
            p = params["lotterylow"]
            mx = np.asarray(A["maxret20"])
            m = ((mx <= p["max_hi"]) & (mom20 >= 0.05) & (close > ma20)
                 & (rng >= 0.5) & tr)
            s = (1.0 - np.nan_to_num(mx)) * 3.0 + np.clip(mom20, 0, 0.3)
            out["lotterylow"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("lotterylow")

    if go("illiq"):
        p = params["illiq"]
        m = ((mom20 >= p["mom_min"]) & (rank >= p["rk_lo"]) & (close > ma20)
             & (rng >= 0.5) & tr)
        s = np.clip(mom20, 0, 0.4) * 2.0 + np.clip(np.nan_to_num(rank) - 0.5, 0, 0.5)
        out["illiq"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("intraday"):
        if has("intraday_ret"):
            p = params["intraday"]
            idr = np.asarray(A["intraday_ret"])
            m = ((_sh(idr) >= p["in_min"] * 0.01 - 1e-9) & (_sh(idr) > 0.005)
                 & (gap <= p["gap_max"]) & (close > ma20) & (rng >= 0.5) & tr)
            s = np.clip(np.nan_to_num(_sh(idr)), 0, 0.1) * 8.0 + np.nan_to_num(rng) * 0.5
            out["intraday"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("intraday")

    if go("engulf"):
        p = params["engulf"]
        po, pc_ = _sh(op), _sh(close)
        yin = (pc_ < po)
        pen = np.where(po > 0, (close - op) / np.maximum(po - pc_, 1e-9), np.nan)
        m = (yin & (close > op) & (close >= po) & (op <= pc_)
             & (pen >= p["pen"] * 0.01 - 1e-9) & (vr >= 1.0) & tr)
        s = np.clip(np.nan_to_num(pen), 0, 3.0) * 0.3 + np.clip(mom20, 0, 0.3)
        out["engulf"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("confluence"):
        p = params["confluence"]
        chks = [
            close > _sh(rh20),
            ((dif > dea) & (_sh(dif) <= _sh(dea))) if dif is not None
            else np.zeros(pc.shape, bool),
            np.nan_to_num(rps50) >= 0.85,
            np.nan_to_num(vr) >= 2.0,
            (mom20 >= 0.05) & (close > ma20),
        ]
        votes = np.zeros(pc.shape, dtype=np.int8)
        for c in chks:
            votes += c.astype(np.int8)
        m = ((votes >= p["need"]) & tr)
        s = votes.astype(np.float32) * 0.4 + np.clip(mom20, 0, 0.4)
        out["confluence"] = (m, np.where(m, s, 0.0).astype(np.float32))

    if go("lhb"):
        if has("lhb_net"):
            # 龙虎榜聪明钱: on the disclosure list TODAY with strong net buy
            # (list publishes after close -> next-open execution = legal T+1)
            p = params["lhb"]
            nb = np.asarray(A["lhb_net"])
            m = ((nb >= p["nb_min"]) & (close > op * 0.995) & tr)
            s = np.clip(np.nan_to_num(nb), 0, 30) * 0.05 + np.clip(pc, 0, 0.1) * 2.0
            out["lhb"] = (m, np.where(m, s, 0.0).astype(np.float32))
        else:
            sleep("lhb")

    # guarantee the full key set for callers that index all families
    for f in FAMILIES:
        if f not in out:
            sleep(f)
    return out
