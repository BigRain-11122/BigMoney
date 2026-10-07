"""REGIME-5 five-state daily regime labeler -- bm-a research lane (T-2026-10-08-177 s1).

Authority: CEO order O-20261007-2215-bm-c sec.1 (criteria direction verbatim
numerified) + frozen contract research/REGIME_STYLE_MATRIX_V1.md sec.1.
Consumer: bm-c scripts/regime_style_matrix.py (takes latest file in
results/regime5_labels/; hysteresis N_CONF=3 is the CONSUMER's confirmation
step -- this file emits RAW daily labels per contract).

Five states (CEO keys verbatim):
  BULL    牛市: above MA200 + new-high density + amount expansion
  CHOP    震荡: range near MA200, mid volatility (default bucket)
  GRIND   阴跌: slow decline + shrinking amount + low volatility
  BEAR    熊市: deep below MA200 (sharp falls live inside this band)
  SUPPORT 护盘期: 50/300ETF volume anomaly + strong-close reversal on a
                 down day (national-team pulse proxy)

FREEZE LAW (frozen v1.0 BEFORE any per-stage return validation -- labels
must never be fitted to outcomes): thresholds below are the CEO direction
quantified with standard round numbers; amendment = validation-batch prereg
only (K>=1000 full-history replay, per-stage differential returns, N_CONF
calibration, transition-cost test = separate prereg slice).

Honest DATA_GAP (declared, not hidden): the intraday tail-pulse face of the
national-team signature needs minute data; minute_feed exists forward-only
(since 2026-10-07), so v1.0 uses the daily proxy = crash-day volume burst
(z-score on 510050/510300 amount) + strong close (close >= low + 0.40*range).
Constituent-stability face = DATA_GAP until a wide intraday panel exists.

Usage:
    python scripts/regime5_labeler.py run       # emit labels (idempotent)
    python scripts/regime5_labeler.py selftest  # hermetic, zero network
Exit codes: 0 = normal, 2 = mechanism fault (reported verbatim, never masked).
"""
import bisect
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL_DIR = os.path.join(ROOT, "results", "regime5_labels")
BENCH = os.path.join(ROOT, "data", "daily", "sh510300.csv")
SUPPORT_BENCH = os.path.join(ROOT, "data", "daily", "sh510050.csv")

# -- frozen v1.0 thresholds (fingerprinted in selftest; amend = prereg) ----
MA_TREND = 200          # CEO direction: MA200 anchor
WARMUP = MA_TREND       # labels start when MA200 fully formed (K honesty)
DIST_BULL = 0.03        # BULL: close >= 3% above MA200
DIST_BEAR = -0.05       # BEAR: close >= 5% below MA200
NH_WIN = 20             # new-high density window (N 日新高密度)
NH_BASE = 60            # rolling high base
NH_TOL = 0.995          # "at the rolling high" tolerance
NH_MIN = 0.50           # >=50% of last 20 days at 60d highs
AMT_FAST, AMT_SLOW = 5, 60   # 成交额扩张: MA5(amount)/MA60(amount)
AMT_EXP_MIN = 1.00      # expansion gate for BULL
R20 = 20
GRIND_R20_MAX = 0.0     # GRIND: 20d return negative (缓步阴线)
GRIND_AMT_MAX = 0.85    # GRIND: amount expansion below neutral (缩量)
VOL_WIN = 20
VOL_PCT_MAX = 0.50      # GRIND: low realized vol (below expanding median)
Z_WIN = 120             # SUPPORT volume z-score window
Z_MIN = 3.0             # 天量异动: amount z >= 3
PULSE_CLOSE = 0.40      # strong close: (close-low)/range >= 0.40
SUPPORT_WIN = 10        # 护盘期 event window after a confirmed pulse day
SUPPORT_DIST_MAX = 0.15 # pulse gate: non-euphoric tape only. v1.0 face fix
                        # (pre-validation, zero return-facing consumption):
                        # 0.03 blocked the canonical 2015-07-06 rescue
                        # (z=5.41 burst + strong close at dist +10.9% --
                        # MA200 lags far below during bubble deflation);
                        # 0.15 keeps euphoric-tape false pulses out while
                        # admitting early-crash rescues.
STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")

THRESHOLDS = {  # canonical freeze fingerprint (selftest t1 asserts equality)
    "ma_trend": MA_TREND, "dist_bull": DIST_BULL, "dist_bear": DIST_BEAR,
    "nh_win": NH_WIN, "nh_base": NH_BASE, "nh_tol": NH_TOL, "nh_min": NH_MIN,
    "amt_fast": AMT_FAST, "amt_slow": AMT_SLOW, "amt_exp_min": AMT_EXP_MIN,
    "r20": R20, "grind_r20_max": GRIND_R20_MAX, "grind_amt_max": GRIND_AMT_MAX,
    "vol_win": VOL_WIN, "vol_pct_max": VOL_PCT_MAX, "z_win": Z_WIN,
    "z_min": Z_MIN, "pulse_close": PULSE_CLOSE, "support_win": SUPPORT_WIN,
    "support_dist_max": SUPPORT_DIST_MAX,
}


def _load(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            try:
                rows.append((r["date"], float(r["close"]),
                             float(r["low"]), float(r["high"]), float(r["amount"])))
            except (KeyError, ValueError):
                continue
    rows.sort(key=lambda x: x[0])
    return rows


def _zseries(vals, win):
    """Rolling z-score, None during warmup. O(n)."""
    out = [None] * len(vals)
    if len(vals) <= win:
        return out
    s = sum(vals[:win])
    sq = sum(v * v for v in vals[:win])
    for i in range(win, len(vals)):
        if i > win:
            s += vals[i - 1] - vals[i - 1 - win]
            sq += vals[i - 1] ** 2 - vals[i - 1 - win] ** 2
        m = s / win
        var = sq / win - m * m
        sd = var ** 0.5
        out[i - 1] = (vals[i - 1] - m) / sd if sd > 0 else None
    return out


def label_series(bench, support_bench):
    """Full-history raw daily labels. Pure function (selftest reuses it)."""
    closes = [r[1] for r in bench]
    lows = [r[2] for r in bench]
    highs = [r[3] for r in bench]
    amts = [r[4] for r in bench]
    n = len(bench)
    rets = [0.0] + [closes[i] / closes[i - 1] - 1.0 if closes[i - 1] else 0.0
                    for i in range(1, n)]
    # rolling features (None = warmup)
    ma200, amt_fast, amt_slow, vol20 = [None] * n, [None] * n, [None] * n, [None] * n
    for i in range(n):
        if i + 1 >= MA_TREND:
            ma200[i] = sum(closes[i - MA_TREND + 1:i + 1]) / MA_TREND
        if i + 1 >= AMT_FAST:
            amt_fast[i] = sum(amts[i - AMT_FAST + 1:i + 1]) / AMT_FAST
        if i + 1 >= AMT_SLOW:
            amt_slow[i] = sum(amts[i - AMT_SLOW + 1:i + 1]) / AMT_SLOW
        if i + 1 >= VOL_WIN:
            w = rets[i - VOL_WIN + 1:i + 1]
            m = sum(w) / VOL_WIN
            vol20[i] = (sum((v - m) ** 2 for v in w) / VOL_WIN) ** 0.5
    # support-bench z by date (aligned calendar join)
    sup_z = {}
    sd_dates = [r[0] for r in support_bench]
    sd_zs = _zseries([r[4] for r in support_bench], Z_WIN)
    for d, z in zip(sd_dates, sd_zs):
        if z is not None:
            sup_z[d] = z
    bench_z = _zseries(amts, Z_WIN)

    labels, diag = [], []
    support_until = -1
    vol_sorted = []   # expanding percentile base (insort, O(log n))
    for i in range(n):
        if i + 1 < WARMUP:
            continue
        dist = closes[i] / ma200[i] - 1.0
        r20 = closes[i] / closes[i - R20] - 1.0
        cnt = 0
        for j in range(i - NH_WIN + 1, i + 1):
            base = max(closes[j - NH_BASE + 1:j + 1])
            if closes[j] >= NH_TOL * base:
                cnt += 1
        nh = cnt / NH_WIN
        amt_exp = amt_fast[i] / amt_slow[i]
        if vol20[i] is not None:
            bisect.insort(vol_sorted, vol20[i])
        vol_pct = (bisect.bisect_right(vol_sorted, vol20[i])
                   / len(vol_sorted))
        d = bench[i][0]
        z_b = bench_z[i]
        z = max((v for v in (z_b, sup_z.get(d)) if v is not None), default=None)
        rng = highs[i] - lows[i]
        strong_close = rng > 0 and (closes[i] - lows[i]) / rng >= PULSE_CLOSE

        if (rets[i] < 0 and z is not None and z >= Z_MIN and strong_close
                and dist < SUPPORT_DIST_MAX):
            support_until = i + SUPPORT_WIN - 1

        if i <= support_until:
            state = "SUPPORT"
        elif dist >= DIST_BULL and nh >= NH_MIN and amt_exp >= AMT_EXP_MIN:
            state = "BULL"
        elif dist <= DIST_BEAR:
            state = "BEAR"
        elif (dist < 0 and r20 < GRIND_R20_MAX and amt_exp < GRIND_AMT_MAX
                and vol_pct <= VOL_PCT_MAX):
            state = "GRIND"
        else:
            state = "CHOP"
        labels.append({"date": d, "state": state})
        diag.append({"date": d, "dist": round(dist, 4), "r20": round(r20, 4),
                     "nh": nh, "amt_exp": round(amt_exp, 4),
                     "vol_pct": round(vol_pct, 4),
                     "amt_z": round(z, 2) if z is not None else None,
                     "state": state})
    return labels, diag


def cmd_run():
    bench = _load(BENCH)
    sup = _load(SUPPORT_BENCH)
    if len(bench) < WARMUP + 100:
        print("regime5_labeler: insufficient bench history "
              f"({len(bench)} bars, need {WARMUP + 100})")
        return 2
    labels, diag = label_series(bench, sup)
    cutoff = bench[-1][0]
    os.makedirs(LABEL_DIR, exist_ok=True)
    out = {"cutoff": cutoff, "source": "REGIME-5 (bm-a)", "labels": labels}
    # contract face: ONLY contract-shaped files live in results/regime5_labels/
    # (consumer takes the latest file in this dir -- diagnostics live elsewhere)
    with open(os.path.join(LABEL_DIR, f"REGIME5-{cutoff}.json"), "w",
              encoding="utf-8", newline="") as fh:
        json.dump(out, fh, ensure_ascii=False)
    counts = {s: sum(1 for L in labels if L["state"] == s) for s in STATES}
    diag_dir = os.path.join(ROOT, "results", "regime5_diag")
    os.makedirs(diag_dir, exist_ok=True)
    with open(os.path.join(diag_dir, f"REGIME5-DIAG-{cutoff}.json"), "w",
              encoding="utf-8", newline="") as fh:
        json.dump({"cutoff": cutoff, "thresholds": THRESHOLDS,
                   "counts": counts, "k_labeled": len(labels),
                   "data_gap": [
                       "intraday tail-pulse face: minute panel forward-only "
                       "(v1.0 daily proxy = crash-day volume z + strong close)",
                       "constituent-stability face: needs wide intraday panel"],
                   "diag_tail": diag[-260:]}, fh, ensure_ascii=False)
    print(f"regime5_labeler: K={len(labels)} labels cutoff={cutoff} "
          + " ".join(f"{s}={c}" for s, c in counts.items()))
    return 0


def _panel_a():
    """Ramp -> crash with TWO pulses (bubble-deflation + deep-bear): BULL/
    BEAR/SUPPORT paths incl. window-override-precedence and wide-dist pulse."""
    bench, price, amt = [], 100.0, 1_000_000.0
    for i in range(320):
        prev = price
        lo_f, hi_f = 0.995, 1.005     # default bar: mid-range close
        if i < 200:              # warmup climb +0.1%/day (MA200 below price)
            price *= 1.001
            amt *= 1.001
        elif i < 260:            # BULL: +0.8%/day ramp, expanding amount
            price *= 1.008
            amt *= 1.03
        elif i == 272:           # PULSE1: bubble-deflation rescue -- down day,
            bench.append(("PULSE1", prev * 0.97, prev * 0.95, prev * 0.985,
                          amt * 15.0))      # dist still > +3% (MA200 lag),
            continue            # 15x burst + strong close -> SUPPORT (v1.0
                               # face fix: widened dist gate admits this)
        elif i < 280:            # BEAR crash: -2.5%/day, deep below MA200,
            price *= 0.975       # weak closes (no pulse on non-pulse days)
            amt *= 1.05
            lo_f, hi_f = 0.999, 1.026
        elif i == 280:           # PULSE2: deep-bear rescue pulse
            bench.append(("PULSE2", prev * 0.98, prev * 0.96, prev * 0.99,
                          amt * 15.0))          # strong close: 2/3 of range
            continue
        else:                    # post-crash flat tail (stays BEAR band)
            price *= 1.0
        bench.append((f"D{i:04d}", price, price * lo_f, price * hi_f, amt))
    sup = [(f"D{i:04d}", 100.0, 99.0, 101.0, 1_000_000.0) for i in range(320)]
    sup[272] = ("PULSE1", 100.0, 99.0, 101.0, 25_000_000.0)
    sup[280] = ("PULSE2", 100.0, 99.0, 101.0, 25_000_000.0)
    return bench, sup


def _panel_c():
    """Gentle decline hugging a flat MA200 from below: pure GRIND bucket."""
    bench = []
    amt = 1_000_000.0
    for i in range(340):
        if i < 200:              # warmup: volatile flat oscillation (high vol)
            price = 100.0 * (1.005 if i % 2 == 0 else 0.995)
        else:                    # grind: -0.04%/day, amount shrinking 8%/day
            price = 100.0 * (0.9996 ** (i - 199)) * (1.0002 if i % 2 == 0
                                                      else 0.9998)
            amt *= 0.92
        bench.append((f"D{i:04d}", price, price * 0.995, price * 1.005, amt))
    sup = [(f"D{i:04d}", 100.0, 99.0, 101.0, 1_000_000.0) for i in range(340)]
    return bench, sup


def _panel_b():
    """Flat tape hugging a flat MA200: pure CHOP bucket."""
    bench = []
    for i in range(340):
        price = 100.0 * (1.003 if i % 2 == 0 else 0.997)
        bench.append((f"D{i:04d}", price, price * 0.999, price * 1.001,
                      1_000_000.0))
    sup = [(f"D{i:04d}", 100.0, 99.0, 101.0, 1_000_000.0) for i in range(340)]
    return bench, sup


def cmd_selftest():
    ok = [0]

    def chk(name, cond):
        ok[0] += 1
        if not cond:
            raise AssertionError(f"selftest FAIL t{ok[0]}: {name}")
        print(f"  t{ok[0]:02d} PASS {name}")

    chk("thresholds freeze fingerprint (v1.0 verbatim)",
        THRESHOLDS == {"ma_trend": 200, "dist_bull": 0.03, "dist_bear": -0.05,
                       "nh_win": 20, "nh_base": 60, "nh_tol": 0.995,
                       "nh_min": 0.50, "amt_fast": 5, "amt_slow": 60,
                       "amt_exp_min": 1.00, "r20": 20, "grind_r20_max": 0.0,
                       "grind_amt_max": 0.85, "vol_win": 20,
                       "vol_pct_max": 0.50, "z_win": 120, "z_min": 3.0,
                       "pulse_close": 0.40, "support_win": 10,
                       "support_dist_max": 0.15})
    bench, sup = _panel_a()
    labels, _diag = label_series(bench, sup)
    by = {L["date"]: L["state"] for L in labels}
    chk("warmup honesty (labels only post-MA200)", len(labels) == 320 - 199)
    chk("BULL path on ramp", by["D0250"] == "BULL")
    chk("BEAR path on deep crash tail", by["D0299"] == "BEAR")
    chk("SUPPORT pulse1 (bubble-deflation, dist in (3%,15%]) labeled",
        by.get("PULSE1") == "SUPPORT")
    chk("SUPPORT pulse2 (deep-bear) labeled", by.get("PULSE2") == "SUPPORT")
    chk("SUPPORT window spans SUPPORT_WIN-1 following days (pulse1)",
        all(by.get(f"D{272 + k:04d}") == "SUPPORT" for k in range(1, 8)
            if 272 + k != 280))
    chk("window override precedence (would-be BEAR day stays SUPPORT)",
        by["D0278"] == "SUPPORT")
    chk("SUPPORT window spans (pulse2 re-extends)",
        all(by.get(f"D{280 + k:04d}") == "SUPPORT" for k in range(1, 10)))
    chk("GRIND path absent in deep-bear tape (priority honesty: BEAR first)",
        all(s in ("BULL", "BEAR", "SUPPORT", "CHOP") for s in by.values()))
    chk("contract label keys exact",
        set(labels[0].keys()) == {"date", "state"})
    l2, _ = label_series(bench, sup)
    chk("determinism (identical rerun)", l2 == labels)
    bench_c, sup_c = _panel_c()
    labels_c, _ = label_series(bench_c, sup_c)
    byc = {L["date"]: L["state"] for L in labels_c}
    chk("GRIND path fires in gentle-decline shrinking-amount low-vol tape",
        byc.get("D0300") == "GRIND" and byc.get("D0319") == "GRIND")
    bench_b, sup_b = _panel_b()
    labels_b, _ = label_series(bench_b, sup_b)
    byb = {L["date"]: L["state"] for L in labels_b}
    chk("CHOP default bucket on flat tape",
        set(byb.values()) == {"CHOP"} and len(labels_b) == 340 - 199)
    chk("state vocabulary exact",
        set(list(by.values()) + list(byb.values()) + list(byc.values()))
        <= set(STATES))
    print("selftest: all PASS")
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "run":
        return cmd_run()
    if mode == "selftest":
        return cmd_selftest()
    print(f"regime5_labeler: unknown mode {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
