"""Strategy x Market FIT MATRIX (user order 2026-09-22:
不同市场并行回测, 策略怎么适合哪个市场, 并行别搞混).

Answers: which strategy fits which market - via ONE standardized full-history
simulation per (strategy, market) cell, ALL MARKETS IN PARALLEL (each market
runs in its own process with its own cache/env/worker pool - zero crosstalk).

  candidates : 31 families x (mid + low + high param variants) + per-market
               incumbent champions; uniform risk (K=5, stop 8%, trail 10%,
               hold<=10d, exposure 90%).
  window     : last 1500 completed days of each market.
  cell       : sharpe / total / excess-vs-bench / maxdd / trades / winrate /
               per-regime contribution breadth.
  outputs    : results/fit_matrix/matrix.md + matrix.json
                - 每策略最优市场  - 每市场最优策略  - 全能榜
More markets join automatically as their caches land (MARKET_SPECS).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"E:\Money")
MARKET_SPECS = [
    ("cn", None, None, 8),
    ("crypto", str(ROOT / "data" / "mkt_crypto" / "cache"),
     str(ROOT / "results_crypto"), 3),
]
WINDOW = 1500
OUT = ROOT / "results" / "fit_matrix"

# module-level worker state (picklable-free: workers import this module
# fresh with the right env already set by the per-market parent process)
_FM = {}


def _init_worker():
    import config as C
    import data as D
    import regime as RG
    _FM["cache"] = D.load_cache(mmap=True)
    _FM["reg"] = RG.compute(_FM["cache"]["bench_sse"],
                            _FM["cache"]["breadth"])


def _eval_cell(g):
    """Module-level (picklable): one standardized simulation of genome g on
    this market's last WINDOW days."""
    import numpy as np
    import backtest as BT
    import data as D
    import strategies as S
    import evolve as EV
    import regime as RG
    gp = EV.decode(g)
    cache = _FM["cache"]
    reg = _FM["reg"]
    T = int(len(cache["dates"]))
    i1 = max(1, T - WINDOW)
    w_any = np.asarray(gp["w"]).max(axis=0) > 1e-4
    needed = [f for f, k in zip(S.FAMILIES, w_any) if k]
    fams = S.family_signals(D.window(cache, i1 - 1, T - 1), gp["params"],
                            fams=needed)
    res = BT.simulate(D.window(cache, i1, T), fams, gp, reg, i1)
    m = res["metrics"]
    bench = np.asarray(cache["bench_csi500"][i1:T], dtype=float)
    if not np.isfinite(bench[0]) or bench[0] <= 0:
        bench = np.asarray(cache["bench_sse"][i1:T], dtype=float)
    bret = float(bench[-1] / bench[0] - 1) if bench[0] > 0 else 0.0
    regs = reg[i1:T]
    rets_d = res["eq"][1:] / res["eq"][:-1] - 1
    contrib = {}
    for i in range(4):
        msk = regs[1:] == i
        if msk.sum() > 5:
            contrib[RG.NAMES[i]] = round(
                float((1 + rets_d[msk]).prod() - 1), 4)
    return {"sharpe": round(m["sharpe"], 3),
            "total": round(m["total"], 4),
            "excess": round(m["total"] - bret, 4),
            "maxdd": round(m["maxdd"], 4),
            "trades": m["n_trades"],
            "win_rate": round(m["win_rate"], 3),
            "regime_contrib": contrib}


def _make_genome(fam, params, K=5, stop=0.08, trail=0.10, hold=10, expo=0.90):
    import numpy as np
    import strategies as S
    import evolve as EV
    g = np.zeros(EV.D_GENOME)
    for idx, (sec, key, kind, args) in enumerate(EV.LAYOUT):
        if sec == "w":
            g[idx] = 1.0 if EV.FAMS[key[1]] == fam else 0.0
        elif sec == "expo":
            g[idx] = (expo - args[0]) / (args[1] - args[0])
        elif sec in ("K", "stop", "trail", "hold"):
            v = {"K": K, "stop": stop, "trail": trail, "hold": hold}[sec]
            g[idx] = (v - args[0]) / (args[1] - args[0])
        elif sec == fam and key in params:
            v = params[key]
            if kind == "pick":
                g[idx] = args.index(v) / max(len(args) - 1, 1)
            else:
                g[idx] = min(max((v - args[0]) / (args[1] - args[0]), 0.0), 1.0)
    return g


def _variants():
    import strategies as S
    out = []
    for f in S.FAMILIES:
        lo_p, mid_p, hi_p = {}, {}, {}
        for (nm, kind, args) in S.SCHEMA[f]:
            if kind == "pick":
                lo_p[nm], mid_p[nm], hi_p[nm] = args[0], args[0], args[-1]
            elif kind == "int":
                lo_p[nm], mid_p[nm], hi_p[nm] = (
                    round(args[0]), round((args[0] + args[1]) / 2),
                    round(args[1]))
            else:
                lo_p[nm], mid_p[nm], hi_p[nm] = (
                    args[0], (args[0] + args[1]) / 2, args[1])
        out.append((f, "mid", mid_p))
        if lo_p != mid_p:
            out.append((f, "low", lo_p))
        if hi_p != mid_p:
            out.append((f, "high", hi_p))
    return out


def _run_market(market, cache_dir, results_dir, n_workers):
    """Parent for one market (its own env -> its own cache + state)."""
    if cache_dir:
        os.environ["MONEY_CACHE_DIR"] = cache_dir
    if results_dir:
        os.environ["MONEY_RESULTS_DIR"] = results_dir
    sys.path.insert(0, str(ROOT))
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    import numpy as np
    import config as C
    import evolve as EV

    cand = [(f, tag, _make_genome(f, p)) for f, tag, p in _variants()]
    try:
        lg = json.load(open(C.RESULTS_DIR / "league.json", encoding="utf-8"))
        for n, st in lg["standings"].items():
            if st.get("champ"):
                cand.append((f"champ_{n}", "live",
                             EV._remap_any(np.asarray(st["champ"],
                                                      dtype=np.float32))))
        live = json.load(open(C.RESULTS_DIR / "live_genome.json",
                              encoding="utf-8"))
        cand.append(("live", "live",
                     EV._remap_any(np.asarray(live["genome"],
                                              dtype=np.float32))))
    except Exception:  # noqa: BLE001
        pass
    print(f"[{market}] {len(cand)}候选 | window={WINDOW}d", flush=True)

    from concurrent.futures import ProcessPoolExecutor
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=n_workers,
                              initializer=_init_worker) as ex:
        for (f, tag, g), cell in zip(cand, ex.map(_eval_cell,
                                                  [c[2] for c in cand])):
            rows.append({"family": f, "variant": tag, **cell})
            print(f"[{market}] {f}/{tag}: 夏普{cell['sharpe']:+.2f} "
                  f"超额{cell['excess']*100:+.1f}pp "
                  f"({cell['trades']}笔)", flush=True)
    with open(OUT / f"cells_{market}.json", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    print(f"[{market}] DONE {len(rows)}格 {time.time()-t0:.0f}s", flush=True)


def _merge():
    cells = {}
    for f in OUT.glob("cells_*.json"):
        cells[f.stem[len("cells_"):]] = json.load(open(f, encoding="utf-8"))
    markets = sorted(cells.keys())
    if not markets:
        print("no cells")
        return
    fams = sorted({r["family"] for rows in cells.values() for r in rows})
    lines = [f"# 策略×市场适配矩阵（近{WINDOW}日全史模拟 · 市场并行）\n"]
    lines.append("| 策略 | 变体 | " + " | ".join(markets) + " | 最适市场 |")
    lines.append("|---|---|" + "---|" * (len(markets) + 1))
    best_per_market = {}
    for fam in fams:
        for v in ("mid", "low", "high", "live"):
            row = {}
            for m in markets:
                r = next((x for x in cells[m] if x["family"] == fam
                          and x["variant"] == v), None)
                if r:
                    row[m] = r
            if not row:
                continue
            scored = {m: row[m]["sharpe"] + 5 * row[m]["excess"]
                      for m in row}
            best = max(scored, key=lambda m: scored[m])
            cur = best_per_market.get(best)
            if cur is None or scored[best] > cur[0]:
                best_per_market[best] = (scored[best], f"{fam}/{v}")
            cells_txt = " | ".join(
                f"夏普{row[m]['sharpe']:+.2f}/超额{row[m]['excess']*100:+.0f}pp"
                if m in row else "-" for m in markets)
            lines.append(f"| {fam} | {v} | {cells_txt} | {best} |")
    lines.append("\n## 每市场最优策略（按 夏普+5×超额）")
    for m, (sc, s) in best_per_market.items():
        lines.append(f"- **{m}**: {s} (score {sc:+.2f})")
    lines.append("\n## 全能榜（全市场正夏普且正超额 = 市场无关真alpha）")
    universal = []
    for fam in fams:
        for v in ("mid", "low", "high", "live"):
            rows = [next((x for x in cells[m] if x["family"] == fam
                          and x["variant"] == v), None) for m in markets]
            if all(rows) and len(markets) >= 2 and \
                    all(r["sharpe"] > 0 and r["excess"] > 0 for r in rows):
                universal.append((sum(r["sharpe"] for r in rows) / len(rows),
                                  fam, v))
    universal.sort(reverse=True)
    for avg, fam, v in universal[:10]:
        lines.append(f"- {fam}/{v}: 平均夏普 {avg:+.2f}（全市场正超额）")
    if not universal:
        lines.append("- （暂无全市场同时正超额策略）")
    (OUT / "matrix.md").write_text("\n".join(lines), encoding="utf-8")
    json.dump(cells, open(OUT / "matrix.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"matrix -> {OUT / 'matrix.md'}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    procs = []
    for market, cache_dir, results_dir, n_workers in MARKET_SPECS:
        env = os.environ.copy()
        p = subprocess.Popen(
            [sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
             "--market", market],
            env=env, stdout=open(OUT / f"run_{market}.log", "w",
                                 encoding="utf-8"),
            stderr=subprocess.STDOUT, cwd=str(ROOT))
        procs.append((market, p))
        print(f"launched: {market} (pid={p.pid})", flush=True)
    for market, p in procs:
        print(f"{market} rc={p.wait()}", flush=True)
    _merge()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--market":
        m = sys.argv[2]
        spec = next(s for s in MARKET_SPECS if s[0] == m)
        _run_market(m, spec[1], spec[2], spec[3])
    else:
        main()
