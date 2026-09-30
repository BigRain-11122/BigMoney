# -*- coding: utf-8 -*-
"""LOWAMP-DEEPSCAN-P1 -- low-amplitude family NEIGHBORHOOD deep-scan (r293 bm-c).

CEO direct order O-2026-09-30-2340 sec.3(bm-c): burn LOWAMP deep-scan on this machine
to deepen T-132 judged-batch input evidence. First N3-face instance per T-133 s2
(neighborhood robustness grids, perpetual faces).

Face: EXPLORATION / neighborhood-robustness evidence. ZERO verdict claims -- T-132
frozen prereg (amp 77-104, topN 2-3, invvol/eq, always-on) is UNTOUCHED; this scan
stresses the NEIGHBORHOOD around that frozen band so the T-132 verdict consumes a
full-neighborhood picture. Deterministic: SEED=20261002, re-runnable byte-stable
(only generated/elapsed are runtime metadata).

Axes vs furnace (LOWAMP-FURNACE-20260930-P1, 1060 cells):
  - systematic NEIGHBORHOOD grid: amp w 55..125 step5 (15) x topN 1..5 x sizing
    {eq, invvol, invamp} x gate {always, bear} = 450 cells (frozen band included:
    w 80-100 x topN 2-3 are grid members -- continuity anchor)
  - random extension: K=2000 draws, amp U[50,130], topN U[1,6] (wider than furnace)
  - dual cost faces x1/x2 derived from same gross/turn series (per side)
  - segment robustness: val window split 2020-2022 / 2023-2025 halves
  - dual nulls (block bootstrap 10000 + sign-flip permutation 10000) top-50
CPU discipline (CEO 2026-09-29 order): self-set BELOW_NORMAL priority, nproc<=26,
BLAS thread caps. O-1820: __main__ guard (no reimport storms)."""
import ctypes
import json
import os
import sys
import traceback
from datetime import datetime
from multiprocessing import Pool, cpu_count

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import numpy as np
import pandas as pd

BASE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(BASE, "data", "consolidation", "adjusted_view")
OUT = os.path.join(BASE, "results", "lowamp_deepscan_p1")
os.makedirs(OUT, exist_ok=True)
LOGP = os.path.join(OUT, "run.log")
COST = 0.001           # per side, x1 face (x2 face derived on same series)
NBOOT = 10000
BLOCK = 21
SEED = 20261002
K_RANDOM = 2000
NPROC = max(1, min(cpu_count() - 4, 26))   # CEO ~10% headroom order

SELFTEST = "--selftest" in sys.argv


def log(m):
    with open(LOGP, "a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), m))


def set_low_priority():
    try:  # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000 (CEO CPU-headroom order)
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def load():
    closes, highs, lows = {}, {}, {}
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".parquet"):
            continue
        sym = fn[:-8]
        df = pd.read_parquet(os.path.join(SRC, fn))
        closes[sym] = df["close"].rename(sym)
        highs[sym] = df["high"].rename(sym)
        lows[sym] = df["low"].rename(sym)
    px = pd.DataFrame(closes).sort_index().dropna(how="all")
    hi = pd.DataFrame(highs).reindex(px.index)
    lo = pd.DataFrame(lows).reindex(px.index)
    log("universe: %d ETFs x %d bars (%s -> %s) [adjusted view]"
        % (px.shape[1], px.shape[0], px.index[0].date(), px.index[-1].date()))
    return px, hi, lo


def stats_from_returns(r):
    r = r.dropna()
    if len(r) < 120:
        return None
    nav = (1.0 + r).cumprod()
    sd = float(r.std())
    return dict(bars=len(r), total=round(float(nav.iloc[-1] - 1.0), 4),
                sharpe=round(float(r.mean() / sd * np.sqrt(252)), 3) if sd > 0 else 0.0,
                maxdd=round(float((nav / nav.cummax() - 1.0).min()), 4),
                hit=round(float((r > 0).mean()), 3))


def _boot(args):
    name, arr, nboot = args
    rng = np.random.default_rng(SEED + sum(ord(c) for c in name))
    T = len(arr)
    nblk = int(np.ceil(T / BLOCK))
    starts = rng.integers(0, T, size=(nboot, nblk))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % T
    idx = idx.reshape(nboot, -1)[:, :T]
    s = arr[idx]
    mu, sd = s.mean(axis=1), s.std(axis=1)
    sh = np.where(sd > 0, mu / sd * np.sqrt(252), 0.0)
    n2 = max(1, T // BLOCK)
    base = arr[: n2 * BLOCK].reshape(n2, BLOCK)
    fl = rng.choice([-1.0, 1.0], size=(nboot, n2))
    nulls = np.empty(nboot)
    for i in range(nboot):
        b = base * fl[i][:, None]
        sd2 = b.std()
        nulls[i] = b.mean() / sd2 * np.sqrt(252) if sd2 > 0 else 0.0
    obs = arr.mean() / arr.std() * np.sqrt(252) if arr.std() > 0 else 0.0
    return name, dict(obs=round(float(obs), 3),
                      p5=round(float(np.percentile(sh, 5)), 3),
                      p95=round(float(np.percentile(sh, 95)), 3),
                      perm_p=round(float((nulls >= obs).mean()), 4))


def main():
    t0 = datetime.now()
    set_low_priority()
    log("LOWAMP-DEEPSCAN-P1 START (neighborhood deep-scan; exploration face; "
        "T-132 input deepening per O-2026-09-30-2340 sec.3; N3 instance per T-133 s2)"
        + (" [SELFTEST]" if SELFTEST else ""))
    px, hi, lo = load()
    ret = px.pct_change()
    amp = (hi / lo - 1.0)
    bench = ret.mean(axis=1).dropna()
    bear = bench < bench.rolling(200).mean()
    b_disc = float((1 + bench.loc["2025-09-24":]).prod() - 1)
    b_val = float((1 + bench.loc["2020-01-01":"2025-09-23"]).prod() - 1)
    log("benchmarks EW19: disc12m %.4f | val 2020-2025 %.4f" % (b_disc, b_val))

    cells = []
    for w in range(55, 126, 5):                       # 15 neighborhood windows
        for topn in (1, 2, 3, 4, 5):
            for gate in ("always", "bear"):
                for sizing in ("eq", "invvol", "invamp"):
                    cells.append((float(w), topn, gate, sizing))
    rng = np.random.default_rng(SEED)
    for _ in range(K_RANDOM):
        cells.append((float(rng.integers(50, 131)), int(rng.integers(1, 7)),
                      str(rng.choice(["always", "bear"])),
                      str(rng.choice(["eq", "invvol", "invamp"]))))
    if SELFTEST:
        cells = cells[:8] + [c for c in cells if c[0] in (90.0,)][:4]
    log("cells total=%d (%d systematic neighborhood + %d random draws)%s"
        % (len(cells), 450, K_RANDOM, " [SELFTEST SUBSET]" if SELFTEST else ""))

    amp_cache = {}
    vol20 = ret.rolling(20).std()

    def run_cell(w, topn, gate, sizing):
        key = int(w)
        if key not in amp_cache:
            amp_cache[key] = amp.rolling(key).mean()
        a = amp_cache[key]
        n_sym = px.shape[1]
        k = max(1, min(int(topn), n_sym))
        ranks = a.rank(axis=1, ascending=True)          # lowest amplitude first
        m = ranks.le(k) & a.notna()
        wgt = m.astype(float)
        wgt = wgt.div(wgt.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        if sizing == "invvol":
            rv = vol20.replace(0, np.nan).fillna(1.0)
            wgt = wgt * (1.0 / rv)
            wgt = wgt.div(wgt.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        elif sizing == "invamp":
            ia = a.replace(0, np.nan)
            wgt = wgt * (1.0 / ia)
            wgt = wgt.div(wgt.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
        if gate == "bear":
            wgt = wgt.mul(bear.reindex(wgt.index).astype(float), axis=0)
        gross = (wgt.shift(1) * ret).sum(axis=1)
        turn = wgt.diff().abs().sum(axis=1)
        turn.iloc[0] = 0.0
        return gross, turn

    rows = []
    series_map = {}
    for i, (w, topn, gate, sizing) in enumerate(cells):
        if i % 250 == 0:
            log("cell %d/%d" % (i, len(cells)))
        gross, turn = run_cell(w, topn, gate, sizing)
        nm = "C%04d" % i
        for costmult, cface in ((1, "x1"), (2, "x2")):
            s = gross - turn * COST * costmult
            series_map[(nm, cface)] = s
        s1 = series_map[(nm, "x1")]
        d = s1.loc["2025-09-24":]
        v = s1.loc["2020-01-01":"2025-09-23"]
        sd_, sv = stats_from_returns(d), stats_from_returns(v)
        if sd_ is None or sv is None:
            continue
        # segment halves on x1 face (x2 total carried for cost-survival reading)
        va = stats_from_returns(s1.loc["2020-01-01":"2022-12-31"])
        vb = stats_from_returns(s1.loc["2023-01-01":"2025-09-23"])
        s2v = stats_from_returns(series_map[(nm, "x2")].loc["2020-01-01":"2025-09-23"])
        bd = bench.reindex(d.dropna().index)
        bv = bench.reindex(v.dropna().index)
        rows.append(dict(name=nm, w=int(w), topn=topn, gate=gate, sizing=sizing,
                         disc=sd_, val=sv,
                         seg_a=va["total"] if va else None,
                         seg_b=vb["total"] if vb else None,
                         val_x2_total=s2v["total"] if s2v else None,
                         beat_disc_pp=round(sd_["total"] - float((1 + bd).prod() - 1), 4),
                         beat_val_pp=round(sv["total"] - float((1 + bv).prod() - 1), 4),
                         robust=bool(sd_["total"] > 0 and sv["total"] > 0
                                     and (va is None or va["total"] > 0)
                                     and (vb is None or vb["total"] > 0))))
    rows.sort(key=lambda x: -x["disc"]["sharpe"])
    log("stats done for %d cell-rows (x1/x2 dual faces computed)" % len(rows))

    # neighborhood-band concentration read: how many cells INSIDE frozen band's
    # neighborhood (w 75-105, topN 2-3, invvol/eq, always) are robust?
    band_cells = [r for r in rows if 75 <= r["w"] <= 105 and r["topn"] in (2, 3)
                  and r["sizing"] in ("invvol", "eq") and r["gate"] == "always"]
    band_robust = sum(1 for r in band_cells if r["robust"])
    band_good = sum(1 for r in band_cells if r["beat_val_pp"] > 0.30)
    log("frozen-band neighborhood face: %d cells, robust %d, beat_val>30pp %d"
        % (len(band_cells), band_robust, band_good))

    nboot = 200 if SELFTEST else NBOOT
    log("dual nulls top-50: %d workers x %d draws" % (NPROC, nboot))
    top50 = [(r["name"] + "|x1", series_map[(r["name"], "x1")].dropna().to_numpy(), nboot)
             for r in rows[:50]]
    with Pool(min(NPROC, 8) if SELFTEST else NPROC) as pool:
        boot = dict(pool.map(_boot, top50))
    log("dual nulls done")

    out = dict(face="EXPLORATION/NEIGHBORHOOD deep-scan (no judgment; T-132 frozen "
                    "prereg untouched; input-evidence deepening per O-2026-09-30-2340 sec.3)",
               directive="O-2026-09-30-2340 sec.3(bm-c) + T-133 s2 N3 instance",
               generated=datetime.now().isoformat(),
               seed=SEED, universe=dict(symbols=int(px.shape[1]), bars=int(px.shape[0])),
               benchmarks=dict(disc12m=round(b_disc, 4), val_2020_2025=round(b_val, 4)),
               n_cells=len(rows), n_base_cells=len(cells),
               band_neighborhood=dict(n=len(band_cells), robust=band_robust,
                                      beat_val_gt30pp=band_good),
               top_by_disc_sharpe=rows[:80], dual_nulls=boot,
               elapsed_sec=round((datetime.now() - t0).total_seconds(), 1))
    suffix = "_selftest" if SELFTEST else ""
    with open(os.path.join(OUT, "stats%s.json" % suffix), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    if not SELFTEST:
        lines = ["# LOWAMP-DEEPSCAN-P1 (neighborhood deep-scan -- exploration, NOT a verdict)", "",
                 "- O-2026-09-30-2340 sec.3 bm-c burn; T-132 verdict-input deepening; N3 instance",
                 "- bench EW19: disc12m %.2f%% | val 2020-2025 %.2f%%" % (b_disc * 100, b_val * 100),
                 "- %d cell-rows (450 neighborhood grid + %d random draws, wider band), dual cost x1/x2, segment halves" % (len(rows), K_RANDOM),
                 "- frozen-band neighborhood (w75-105 x topN2-3 x invvol/eq x always): %d cells, robust %d, beat_val>30pp %d" % (len(band_cells), band_robust, band_good), "",
                 "| cell | amp_w | topN | gate | sizing | disc12m% | disc sh | val20-25% | val sh | segA% | segB% | valx2% | robust | p5-p95 | perm_p |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows[:25]:
            b = boot.get(r["name"] + "|x1", {})
            lines.append("| %s | %s | %s | %s | %s | %.2f | %.2f | %.2f | %.2f | %s | %s | %s | %s | %s | %s |"
                         % (r["name"], r["w"], r["topn"], r["gate"], r["sizing"],
                            r["disc"]["total"] * 100, r["disc"]["sharpe"],
                            r["val"]["total"] * 100, r["val"]["sharpe"],
                            "%.1f" % (r["seg_a"] * 100) if r["seg_a"] is not None else "-",
                            "%.1f" % (r["seg_b"] * 100) if r["seg_b"] is not None else "-",
                            "%.1f" % (r["val_x2_total"] * 100) if r["val_x2_total"] is not None else "-",
                            r["robust"],
                            ("%s..%s" % (b.get("p5", "-"), b.get("p95", "-"))) if b else "-",
                            b.get("perm_p", "-") if b else "-"))
        lines += ["", "## Honest notes", "- exploration face: selection-bias law applies; true out-of-sample = T-132 judged face (frozen prereg, K>=1000 virtual starts, dual nulls, x2 cost)",
                  "- Top-2/3 concentration = single-name risk face; liquidity/tradability entry gates belong to the T-132 judged face (frozen there)",
                  "- 19-ETF small universe; panel starts 2020 (no pre-2020 face on this universe)"]
        with open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    log("DONE elapsed %.1fs -> stats%s.json%s" % (out["elapsed_sec"], suffix, " + summary.md" if not SELFTEST else ""))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open(LOGP, "a", encoding="utf-8") as f:
            f.write("[%s] FATAL\n%s\n" % (datetime.now().isoformat(), traceback.format_exc()))
        raise SystemExit(2)
