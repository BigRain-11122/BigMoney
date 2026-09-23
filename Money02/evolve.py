"""Hang-immune evaluation layer + GA + walk-forward.

Evaluator (2026-09-19 用户令"假死卡死就自己重构"后的重构):
- mp.Pool 的致命缺陷 = worker 死亡(OOM)时 pool.map 永久挂起且无异常。
  重构为 concurrent.futures.ProcessPoolExecutor：worker 死亡会抛
  BrokenProcessPool 而非挂死。
- 批次整体 deadline：超时/BrokenPool -> worker 数减半、重建池、重试该批
  （最多降级 3 次，下限 2 worker），每次降级记录日志 = 自愈。
- 启动时按可用内存自适应 worker 数（本机常驻仅 ~5GB 空余）。
"""
import ctypes
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, BrokenExecutor
from concurrent.futures.process import BrokenProcessPool

import numpy as np

import config as C
import data as D
import strategies as S
import regime as RG
import backtest as BT

FAMS = list(S.FAMILIES)
N_REG = RG.N_REGIMES
LAYOUT = []
for f in FAMS:
    for (nm, kind, args) in S.SCHEMA[f]:
        LAYOUT.append((f, nm, kind, args))
for r in range(N_REG):
    for fi in range(len(FAMS)):
        LAYOUT.append(("w", (r, fi), "f", [0.0, 1.0]))
for r in range(N_REG):
    LAYOUT.append(("expo", r, "f", [0.25, 1.0]))
LAYOUT.append(("K", None, "int", [2, 10]))
LAYOUT.append(("stop", None, "f", [0.03, 0.12]))
LAYOUT.append(("trail", None, "f", [0.03, 0.15]))
LAYOUT.append(("hold", None, "int", [3, 15]))
D_GENOME = len(LAYOUT)

# ---- 旧基因语义重映射 (2026-09-21 家族扩容8→18) ------------------------
# Old 8-family layouts stored in live_genome.json / league champs / mem are
# POSITIONALLY incompatible with the expanded LAYOUT. _expand_old() remaps
# them semantically: old params/weights/exposure/risk land at their family's
# NEW slots, new families get weight 0 -> behavior is bit-identical, and
# evolution then explores the 10 new families via mutation.
OLD_FAMS = ["breakout", "limitup", "meanrev", "pullback", "smallmom",
            "relstr", "nrev", "volburst"]
FAMS_18 = OLD_FAMS + ["vcp", "gapup", "streak", "newhigh250", "macd",
                      "lowvol", "turnspike", "bollrev", "crashst", "diplimit"]
FAMS_30 = FAMS_18 + ["kdjgold", "ccirev", "wrrev", "mfidip", "atrbreak",
                     "adxstrong", "momspeed", "lotterylow", "illiq",
                     "intraday", "engulf", "confluence"]


def _legacy_layout(fams):
    L = []
    for f in fams:
        for (nm, kind, args) in S.SCHEMA[f]:
            L.append((f, nm, kind, args))
    for r in range(N_REG):
        for fi in range(len(fams)):
            L.append(("w", (r, fi), "f", [0.0, 1.0]))
    for r in range(N_REG):
        L.append(("expo", r, "f", [0.25, 1.0]))
    L.append(("K", None, "int", [2, 10]))
    L.append(("stop", None, "f", [0.03, 0.12]))
    L.append(("trail", None, "f", [0.03, 0.15]))
    L.append(("hold", None, "int", [2, 15]))
    return L


_LEGACY_LEN = {len(_legacy_layout(fs)): fs for fs in (OLD_FAMS, FAMS_18, FAMS_30)}
_SLOT = {}
for idx, (sec, key, kind, args) in enumerate(LAYOUT):
    _SLOT.setdefault((sec, key), idx)


def _remap_any(g):
    """Remap any known legacy-generation gene vector into the current space.
    New-family params get mid-range genes; new-family weights stay 0.0 so the
    remapped genome behaves exactly like the original."""
    g = np.clip(np.asarray(g, dtype=np.float64), 0.0, 1.0)
    if len(g) == D_GENOME:
        return g
    fams = _LEGACY_LEN.get(len(g))
    if fams is None:
        raise ValueError(f"unknown legacy genome length {len(g)} "
                         f"(known: {sorted(_LEGACY_LEN)}, now {D_GENOME})")
    src = _legacy_layout(fams)
    out = np.full(D_GENOME, 0.5)
    w_new = np.zeros((N_REG, len(FAMS)))
    for idx, (sec, key, kind, args) in enumerate(src):
        u = g[idx]
        if sec in FAMS:
            out[_SLOT[(sec, key)]] = u
        elif sec == "w":
            w_new[key] = u
        else:
            out[_SLOT[(sec, key)]] = u
    for r in range(N_REG):
        for fi in range(len(FAMS)):
            out[_SLOT[("w", (r, fi))]] = w_new[r, fi]
    return out

_W = {}


CLANS = {  # 门派联赛: style-exclusive clans (user orders: diverse PK 09-20;
    # 极度细分流派海选+交叉融合 2026-09-21)
    "momentum": ["breakout", "volburst", "relstr", "vcp", "gapup",
                 "streak", "newhigh250", "atrbreak", "adxstrong",
                 "momspeed", "lotterylow", "intraday"],
    "reversal": ["meanrev", "nrev", "bollrev", "crashst", "diplimit",
                 "kdjgold", "ccirev", "wrrev", "mfidip", "engulf"],
    "board": ["limitup", "smallmom", "turnspike", "illiq", "lhb"],
    "trendpull": ["pullback", "breakout", "macd", "lowvol"],
    "allround": None,  # open class: all families + confluence 融合流独家
}
CLAN_CN = {"momentum": "动量突破派", "reversal": "超跌反转派",
           "board": "打板接力派", "trendpull": "趋势回调派",
           "allround": "全能混权派"}
REG_CN = {"bull": "多头", "chop": "震荡", "crash": "急跌", "rebound": "修复"}
BENCH_CN = {"csi500": "中证500", "sse": "上证综指"}
# 实盘席位加权 (user order 2026-09-21: 实盘成绩的权重要提高):
# the incumbent's REAL paper excess since taking the seat raises the
# challenger bar -> live results speak louder than backtest fitness, and a
# base margin stops noise-driven seat flips so live records can accumulate.
SEAT_BASE = 0.05
SEAT_LIVE_W = 0.10
SEAT_MARGIN_LO, SEAT_MARGIN_HI = -0.5, 1.5


def _clan_mask(names):
    return None if names is None else [f in names for f in FAMS]


def decode(g, fam_mask=None):
    g = np.clip(np.asarray(g, dtype=np.float64), 0.0, 1.0)
    if len(g) != D_GENOME:
        g = _remap_any(g)
    params = {f: {} for f in FAMS}
    w = np.zeros((N_REG, len(FAMS)))
    expo = np.zeros(N_REG)
    K = stop = trail = hold = None
    for idx, (sec, key, kind, args) in enumerate(LAYOUT):
        u = g[idx]
        if kind == "f":
            v = args[0] + u * (args[1] - args[0])
        elif kind == "int":
            v = int(round(args[0] + u * (args[1] - args[0])))
        else:
            v = args[min(int(u * len(args)), len(args) - 1)]
        if sec in FAMS:
            params[sec][key] = v
        elif sec == "w":
            w[key] = v
        elif sec == "expo":
            expo[key] = v
        elif sec == "K":
            K = v
        elif sec == "stop":
            stop = v
        elif sec == "trail":
            trail = v
        elif sec == "hold":
            hold = v
    if fam_mask is not None:
        w[:, ~np.asarray(fam_mask, dtype=bool)] = 0.0  # style-exclusive lane
    w = w / np.maximum(w.sum(axis=1, keepdims=True), 1e-6)
    return {"params": params, "w": w, "exposure": expo, "K": K,
            "stop": stop, "trail": trail, "hold": hold}


def _init_worker():
    _W["cache"] = D.load_cache(mmap=True)
    _W["regime"] = RG.compute(_W["cache"]["bench_sse"], _W["cache"]["breadth"])


def _eval(task):
    g, i0, i1, detail, mask = task
    gp = decode(g, fam_mask=mask)
    cache = _W["cache"]
    # selective computation: only families this genome actually weights
    # (any regime) - keeps a 30-family space at 8-family eval cost
    w_any = np.asarray(gp["w"]).max(axis=0) > 1e-4
    fams = S.family_signals(D.window(cache, i0 - 1, i1 - 1), gp["params"],
                            fams=[f for f, k in zip(S.FAMILIES, w_any) if k])
    res = BT.simulate(D.window(cache, i0, i1), fams, gp, _W["regime"], i0)
    m = res["metrics"]
    fit = BT.fitness(m)
    if detail:
        return (np.asarray(g).tolist(), m, np.asarray(res["eq"]).tolist(),
                res["trades"], res["invested"].tolist())
    return (fit, m["n_trades"], m["sharpe"], m["maxdd"], m["cagr"])


def _free_ram_gb():
    try:  # Windows
        class MEMSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = MEMSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        return ms.ullAvailPhys / 1e9
    except Exception:  # noqa: BLE001
        return 8.0


class Evaluator:
    """Hang-immune genome evaluator: broken/timeout -> degrade & retry."""

    def __init__(self, n_proc=None):
        n_cpu = os.cpu_count() or 8
        by_ram = max(2, int(_free_ram_gb() / 0.35))
        self.n_proc = min(n_proc or 12, n_cpu - 2, by_ram)
        self.n_proc = max(2, self.n_proc)
        self.degrades = 0
        self._build()

    def _build(self):
        self.ex = ProcessPoolExecutor(max_workers=self.n_proc,
                                      initializer=_init_worker)

    def _degrade(self, reason):
        self.degrades += 1
        if self.degrades > 3:
            raise RuntimeError(f"evaluator degraded too often: {reason}")
        try:
            self.ex.shutdown(wait=False, cancel_futures=True)
        except Exception:  # noqa: BLE001
            pass
        self.n_proc = max(2, self.n_proc // 2)
        print(f"[evaluator] DEGRADE -> {self.n_proc} workers ({reason})", flush=True)
        self._build()

    def map(self, tasks, deadline_s=420.0):
        """Evaluate tasks; on hang/timeout/dead-worker degrade and retry once
        per degradation level. Never blocks forever."""
        t0 = time.time()
        while True:
            try:
                futs = [self.ex.submit(_eval, t) for t in tasks]
                out = []
                for f in futs:
                    left = deadline_s - (time.time() - t0)
                    if left <= 0:
                        raise TimeoutError("batch deadline")
                    out.append(f.result(timeout=left))
                return out
            except (BrokenProcessPool, BrokenExecutor, TimeoutError, OSError) as e:
                if self.degrades >= 3:
                    raise
                self._degrade(type(e).__name__)
                t0 = time.time()

    def close(self):
        try:
            self.ex.shutdown(wait=False, cancel_futures=True)
        except Exception:  # noqa: BLE001
            pass


def _tourn(rng, fit):
    idx = rng.integers(0, len(fit), size=C.TOURN)
    return int(idx[np.argmax(fit[idx])])


def _crossover(rng, a, b):
    mask = rng.random(D_GENOME) < 0.5
    child = np.where(mask, a, b)
    if rng.random() < 0.3:
        child = 0.7 * child + 0.3 * (a + b) / 2.0
    return child.astype(np.float32)


def _mutate(rng, x):
    m = rng.random(D_GENOME) < C.MUT_P
    if m.any():
        x[m] = np.clip(x[m] + rng.normal(0, C.MUT_SIG, int(m.sum())), 0, 1)


def run_ga(ev, i0, i1, pop=None, gens=None, seed=0, init=None, verbose=False,
           mask=None):
    pop = pop or C.POP
    gens = gens if gens is not None else C.GENS_MAX
    rng = np.random.default_rng(seed)
    X = rng.random((pop, D_GENOME), dtype=np.float32)
    if init:
        ne = min(len(init), pop // 2)
        for gi in range(ne):
            X[gi] = np.clip(_remap_any(np.asarray(init[gi], dtype=np.float32)), 0, 1)
        for gi in range(ne, min(2 * ne, pop)):
            X[gi] = np.clip(X[gi - ne] + rng.normal(0, 0.08, D_GENOME), 0, 1)
            X[gi] = np.asarray(X[gi], dtype=np.float32)
    out = ev.map([(X[k], i0, i1, False, mask) for k in range(pop)])
    fit = np.array([o[0] for o in out], dtype=np.float64)
    best_hist = [float(fit.max())]
    for gen in range(gens):
        if len(best_hist) > C.PLATEAU and \
           max(best_hist[-C.PLATEAU:]) <= best_hist[-C.PLATEAU - 1] + 1e-4:
            break
        order = np.argsort(-fit)
        newX = [X[i].copy() for i in order[:C.ELITE]]
        while len(newX) < pop:
            a = _tourn(rng, fit)
            b = _tourn(rng, fit)
            child = _crossover(rng, X[a], X[b])
            _mutate(rng, child)
            newX.append(child)
        X = np.stack(newX).astype(np.float32)
        child_out = ev.map([(X[k], i0, i1, False, mask)
                            for k in range(C.ELITE, pop)])
        fit = np.concatenate([fit[order[:C.ELITE]],
                              np.array([o[0] for o in child_out])])
        best_hist.append(float(fit.max()))
        if verbose:
            print(f"    gen{gen + 1} best={fit.max():.3f}")
    order = np.argsort(-fit)
    best = X[order[0]].copy()
    elites = [X[i].tolist() for i in order[:6]]
    return best, float(fit[order[0]]), elites, best_hist
def make_folds(T):
    folds = []
    i0 = C.START_OFFSET
    while i0 + C.TRAIN_DAYS + C.TEST_DAYS <= T:
        i1 = i0 + C.TRAIN_DAYS
        j1 = i1 + C.TEST_DAYS
        folds.append((i0, i1, j1))
        i0 += C.TEST_DAYS
    return folds


def _bench_seg(cache, i1, j1, key):
    b = np.asarray(cache[key][i1:j1], dtype=np.float64)
    if len(b) == 0 or not np.isfinite(b[0]) or b[0] <= 0:
        return None
    return b / b[0]


def run_walkforward(tag="wf", max_minutes=None, pop=None, gens=None,
                    n_folds=None, n_proc=None, out_dir=None):
    """Full walk-forward evolution pass. Writes fold records + summary to
    results/<tag>/ and returns the summary dict."""
    max_minutes = max_minutes or C.WF_BUDGET_MIN
    cache = D.load_cache()
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    folds = make_folds(T)
    if n_folds:
        folds = folds[-n_folds:]
    out_dir = out_dir or (C.RESULTS_DIR / tag)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    records = []
    elites = None
    best_g = None
    ev = Evaluator(n_proc)
    try:
        for fi, (i0, i1, j1) in enumerate(folds):
            if best_g is not None and (time.time() - t0) > max_minutes * 60:
                print(f"  [budget] fold {fi} reuses previous genome")
            else:
                best_g, best_f, elites, hist = run_ga(
                    ev, i0, i1, pop=pop, gens=gens, seed=C.SEED + fi, init=elites)
            gp = decode(best_g)
            fams = S.family_signals(D.window(cache, i1 - 1, j1 - 1), gp["params"])
            res = BT.simulate(D.window(cache, i1, j1), fams, gp, reg, i1)
            m = res["metrics"]
            d0 = str(cache["dates"][i1]); d1 = str(cache["dates"][j1 - 1])
            b300 = _bench_seg(cache, i1, j1, "bench_hs300")
            rec = {
                "fold": fi, "train": [i0, i1], "test": [i1, j1],
                "test_dates": [str(x) for x in np.asarray(cache["dates"][i1:j1])],
                "start": d0, "end": d1,
                "eq": np.asarray(res["eq"]).tolist(),
                "invested": np.asarray(res["invested"]).tolist(),
                "trades": res["trades"],
                "metrics": m,
                "bench_hs300": (b300.tolist() if b300 is not None else None),
                "genome": np.asarray(best_g).tolist(),
                "params": {f: dict(gp["params"][f]) for f in FAMS},
                "w": np.asarray(gp["w"]).tolist(),
                "exposure": np.asarray(gp["exposure"]).tolist(),
            }
            records.append(rec)
            with open(out_dir / f"fold_{fi:03d}.json", "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False)
            print(f"  fold {fi:02d} {d0}..{d1} OOS ret={m['total'] * 100:6.2f}% "
                  f"sharpe={m['sharpe']:5.2f} maxdd={m['maxdd'] * 100:6.2f}% "
                  f"trades={m['n_trades']:3d} | {time.time() - t0:6.0f}s", flush=True)

        # final live genome: train on the most recent window ending at T
        live_i0 = max(0, T - C.TRAIN_DAYS)
        live_g, live_f, _, _ = run_ga(ev, live_i0, T, pop=pop or C.POP,
                                      gens=gens if gens is not None else C.GENS_MAX,
                                      seed=C.SEED + 9999, init=elites)
    finally:
        ev.close()
    live_gp = decode(live_g)
    live = {"genome": np.asarray(live_g).tolist(),
            "params": {f: dict(live_gp["params"][f]) for f in FAMS},
            "w": np.asarray(live_gp["w"]).tolist(),
            "exposure": np.asarray(live_gp["exposure"]).tolist(),
            "K": int(live_gp["K"]), "stop": live_gp["stop"],
            "trail": live_gp["trail"], "hold": int(live_gp["hold"]),
            "trained_through": str(np.asarray(cache["dates"])[-1])}
    with open(out_dir / "live_genome.json", "w", encoding="utf-8") as f:
        json.dump(live, f, ensure_ascii=False, indent=2)
    with open(C.RESULTS_DIR / "live_genome.json", "w", encoding="utf-8") as f:
        json.dump(live, f, ensure_ascii=False, indent=2)

    summary = {"tag": tag, "n_folds": len(records),
               "train_days": C.TRAIN_DAYS, "test_days": C.TEST_DAYS,
               "elapsed_s": round(time.time() - t0, 1), "records": len(records)}
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return {"records": records, "live": live, "cache": cache, "regime": reg,
            "out_dir": out_dir, "summary": summary}


def _load_live():
    p = C.RESULTS_DIR / "live_genome.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
    return None


def _hof_path():
    return C.RESULTS_DIR / "halloffame.json"


def _load_hof():
    p = _hof_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return []


def _save_hof(hof):
    with open(_hof_path(), "w", encoding="utf-8") as f:
        json.dump(hof[:12], f, ensure_ascii=False, indent=1)


def random_evolve(rounds=8, pop=24, gens=2, n_proc=None, budget_minutes=5.5):
    """疯狂迭代 mode (user order 2026-09-19): each round samples a RANDOM
    historical point -> quick GA on the 480d window (seeded from hall-of-fame
    + live genome) -> validate the best on the unseen 60d AFTER the window.
    Champions ranked by VALIDATION score across regimes (anti-overfit); the
    live genome = top validator that ALSO scores best on the latest window
    (cross-time champion). Time-budgeted: as many rounds as fit."""
    cache = D.load_cache()
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    live = _load_live()
    hof = _load_hof()
    t0 = time.time()
    rng = np.random.default_rng(int(time.time() * 1000) & 0xFFFFFF)
    ev = Evaluator(n_proc)
    log = []
    r = 0
    champ_g = np.asarray(live["genome"], dtype=np.float32) if live and live.get("genome") \
        else np.random.default_rng(0).random(D_GENOME, dtype=np.float32)
    champ_fit = -1e18
    try:
        while r < rounds and (time.time() - t0) < budget_minutes * 60:
            i0 = int(rng.integers(C.START_OFFSET,
                                  max(C.START_OFFSET + 1, T - C.TRAIN_DAYS - C.TEST_DAYS)))
            i1 = i0 + C.TRAIN_DAYS
            seed = [e["genome"] for e in hof[:4]] + \
                   ([live["genome"]] if live and live.get("genome") else [])
            best_g, _, _, _ = run_ga(ev, i0, i1, pop=pop, gens=gens,
                                     seed=int(rng.integers(1 << 30)), init=seed)
            gp = decode(best_g)
            fams = S.family_signals(D.window(cache, i1 - 1, i1 + C.TEST_DAYS - 1),
                                    gp["params"])
            res = BT.simulate(D.window(cache, i1, i1 + C.TEST_DAYS), fams, gp, reg, i1)
            m = res["metrics"]
            val = BT.fitness(m)
            bench = np.asarray(cache["bench_csi500"][i1:i1 + C.TEST_DAYS],
                               dtype=np.float64)
            bench_ret = float(bench[-1] / bench[0] - 1) if len(bench) > 1 and \
                np.isfinite(bench[0]) and bench[0] > 0 else 0.0
            excess = m["total"] - bench_ret
            hof.append({"genome": np.asarray(best_g).tolist(),
                        "val_fit": round(float(val), 4),
                        "val_ret": round(m["total"], 4),
                        "val_excess": round(float(excess), 4),
                        "val_bench": round(bench_ret, 4),
                        "val_sharpe": round(m["sharpe"], 3),
                        "val_maxdd": round(m["maxdd"], 4),
                        "val_trades": m["n_trades"],
                        "window": [str(cache["dates"][i1]),
                                   str(cache["dates"][i1 + C.TEST_DAYS - 1])]})
            log.append({"round": r, "val_fit": round(float(val), 4),
                        "val_ret": round(m["total"], 4),
                        "val_excess": round(float(excess), 4),
                        "window": hof[-1]["window"]})
            r += 1
        # rank by benchmark-relative strength: survival fitness + excess vs csi500
        hof = sorted(hof, key=lambda e: -(e.get("val_fit", 0)
                                          + e.get("val_excess", 0)))[:12]
        _save_hof(hof)
        # champion selection: top validators re-scored on the LATEST window
        cands = [e["genome"] for e in hof[:4]]
        if live and live.get("genome"):
            cands.append(live["genome"])
        outs = ev.map([(np.asarray(g, dtype=np.float32),
                        T - C.TRAIN_DAYS, T, False, None) for g in cands])
        best_i = int(np.argmax([o[0] for o in outs]))
        champ_g = cands[best_i]
        champ_fit = float(outs[best_i][0])
    finally:
        ev.close()
    gp = decode(champ_g)
    live = {"genome": np.asarray(champ_g).tolist(),
            "params": {f: dict(gp["params"][f]) for f in FAMS},
            "w": np.asarray(gp["w"]).tolist(),
            "exposure": np.asarray(gp["exposure"]).tolist(),
            "K": int(gp["K"]), "stop": gp["stop"], "trail": gp["trail"],
            "hold": int(gp["hold"]),
            "trained_through": str(np.asarray(cache["dates"])[-1]),
            "fit": round(champ_fit, 4), "rounds": r,
            "hof_best_val": (hof[0]["val_fit"] if hof else None)}
    with open(C.RESULTS_DIR / "live_genome.json", "w", encoding="utf-8") as f:
        json.dump(live, f, ensure_ascii=False, indent=2)
    return {"live": live, "cache": cache, "regime": reg,
            "out_dir": C.RESULTS_DIR / "latest",
            "rounds": r, "log": log, "champ_fit": champ_fit}


def _league_path():
    return C.RESULTS_DIR / "league.json"


def _league_default():
    return {n: {"pts": 0, "rounds": 0, "sum_excess": 0.0,
                "sum_ret": 0.0, "wins": 0, "champ": None,
                "champ_score": -1e9, "best_val": -1e9, "best_val_ret": None,
                "best_val_window": None, "mem": []} for n in CLANS}


def _load_league():
    p = _league_path()
    if p.exists():
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            base = _league_default()  # schema-upgrade-safe normalization
            src = raw.get("standings", raw) if isinstance(raw, dict) else {}
            if not isinstance(src, dict):
                src = {}
            for n, st in src.items():
                if n in base and isinstance(st, dict):
                    for k, v in st.items():
                        if k in base[n] or k == "champ_score":
                            base[n][k] = v
            return base
        except Exception:  # noqa: BLE001
            pass
    return _league_default()


def _rounds_path():
    return C.RESULTS_DIR / "league_rounds.jsonl"


def _load_meta(league):
    """League meta = 机制迭代的记忆体: valid-round count, regime coverage,
    per-clan-per-regime record, seat history, recent rounds. Bootstraps
    round numbering from accumulated standings when upgrading an old
    league.json (schema-upgrade-safe)."""
    meta = {}
    p = _league_path()
    if p.exists():
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("meta"), dict):
                meta = raw["meta"]
        except Exception:  # noqa: BLE001
            pass
    if not meta:
        meta = {"n_valid": int(max((st.get("rounds", 0)
                                    for st in league.values()), default=0))}
    meta.setdefault("n_valid", 0)
    meta.setdefault("regime_cov", {n: 0 for n in RG.NAMES})
    meta.setdefault("clan_regime", {})
    meta.setdefault("seat_log", [])
    meta.setdefault("recent", [])
    return meta


def _majority_regime(reg, i1, j1):
    seg = np.asarray(reg[i1:j1], dtype=np.int8)
    if not len(seg):
        return 1
    return int(np.bincount(seg, minlength=RG.N_REGIMES).argmax())


def _pick_window(cache, reg, meta, rng):
    """赛程迭代: draw 32 candidate windows, prefer the least-covered
    test-window regime (random tie-break) so the league systematically
    samples every market state instead of randomly re-visiting one.
    Same window for all clans - fairness untouched."""
    T = int(len(cache["dates"]))
    cov = meta.get("regime_cov", {})
    lo = C.START_OFFSET
    hi = max(lo + 1, T - C.TRAIN_DAYS - C.TEST_DAYS)
    best = None
    for _ in range(32):
        i0 = int(rng.integers(lo, hi))
        i1 = i0 + C.TRAIN_DAYS
        j1 = i1 + C.TEST_DAYS
        r = _majority_regime(reg, i1, j1)
        key = (int(cov.get(RG.NAMES[r], 0)), float(rng.random()))
        if best is None or key < best[0]:
            best = (key, i0, i1, j1, r)
    return best[1], best[2], best[3], best[4]


def _paper_excess_since(cache, live):
    """Real paper-trading excess of the incumbent LIVE genome since it took
    the seat (user order 2026-09-21: 实盘成绩权重提高). Returns (excess,
    base_date) or (None, None) when no executed history exists yet."""
    p = C.RESULTS_DIR / "paper.json"
    if not p.exists():
        return None, None
    try:
        paper = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None, None
    hist = paper.get("history") or []
    if not hist:
        return None, None
    dates = [str(x) for x in np.asarray(cache["dates"])]
    last_d = str(hist[-1]["date"])
    if last_d not in dates:
        return None, None
    seat_d = (live or {}).get("seat_date")
    if seat_d and seat_d in dates:
        bi = max(dates.index(seat_d) - 1, 0)  # equity base = close before seat
        base_d = dates[bi]
        base_eq = float(C.CAPITAL)
        for h in hist:
            if str(h["date"]) <= base_d:
                base_eq = float(h["equity"])
    else:
        base_d, base_eq = str(hist[0]["date"]), float(C.CAPITAL)
    if base_d not in dates or base_eq <= 0:
        return None, None
    li, bi2 = dates.index(last_d), dates.index(base_d)
    if li <= bi2:
        return None, None
    bench = np.asarray(cache["bench_csi500"][bi2:li + 1], dtype=np.float64)
    if not np.isfinite(bench[0]) or bench[0] <= 0:
        bench = np.asarray(cache["bench_sse"][bi2:li + 1], dtype=np.float64)
    bret = float(bench[-1] / bench[0] - 1) if bench[0] > 0 else 0.0
    pret = float(hist[-1]["equity"]) / base_eq - 1.0
    return round(pret - bret, 4), base_d


def _save_league(league, meta, round_log=None):
    with open(_league_path(), "w", encoding="utf-8") as f:
        json.dump({"standings": league, "meta": meta, "last_round": round_log},
                  f, ensure_ascii=False, indent=1)
    lines = ["# 门派联赛（同窗盲测对战 · 每10分钟一轮 · 赛制逐轮总结迭代）\n"]
    lines.append("## 积分榜\n")
    lines.append("| 门派 | 积分 | 轮次 | 跑赢基准率 | 平均超额 | 平均收益 | 最佳盲测 | 记忆 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for n, st in sorted(league.items(), key=lambda kv: -kv[1]["pts"]):
        wr = st["wins"] / max(st["rounds"], 1) * 100
        bv, bw = st.get("best_val_ret"), st.get("best_val_window")
        best = f"{bv * 100:+.1f}%@{str(bw[0])}" if (bv is not None and bw) else "-"
        lines.append(f"| {CLAN_CN[n]} | **{st['pts']}** | {st['rounds']} | "
                     f"{wr:.0f}% | {st['sum_excess'] / max(st['rounds'], 1) * 100:+.2f}pp | "
                     f"{st['sum_ret'] / max(st['rounds'], 1) * 100:+.2f}% | "
                     f"{best} | {len(st.get('mem', []))}条 |")
    recent = meta.get("recent", [])
    if recent:
        lines.append("\n## 最近轮次\n")
        lines.append("| 轮 | 盲测窗口 | 市道 | 基准 | 本轮冠军 | 冠军超额 | 席位 |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in recent[-12:]:
            seat = (f"易主→{CLAN_CN.get(r['seat_holder'], r['seat_holder'])}"
                    if r.get("seat_change") else "现役保持")
            bsrc = BENCH_CN.get(r.get("bench_src"), "中证500")
            lines.append(f"| {r['round']} | {r['window'][0]}~{r['window'][1]} | "
                         f"{REG_CN.get(r['regime'], r['regime'])} | "
                         f"{bsrc} {r['bench_ret'] * 100:+.1f}% | "
                         f"{CLAN_CN.get(r['winner'], r['winner'])} | "
                         f"{r['win_excess'] * 100:+.1f}pp | {seat} |")
    if round_log:
        n = round_log.get("round", meta.get("n_valid", 0))
        lines.append(f"\n## 第{n}轮总结（{round_log['window'][0]}~"
                     f"{round_log['window'][1]} 盲测）\n")
        co = "（共载降额）" if round_log.get("co_load") else ""
        bsrc = BENCH_CN.get(round_log.get("bench_src"), "中证500")
        lines.append(f"- 市道：{REG_CN.get(round_log.get('regime'), round_log.get('regime'))}｜"
                     f"基准{bsrc} {round_log['bench_ret'] * 100:+.1f}%｜"
                     f"预算 种群{round_log['pop']}×{round_log['gens']}代{co}")
        for c in sorted(round_log["clans"], key=lambda x: -x["excess"]):
            bonus = (("跑赢+3 " if c["excess"] > 0 else "")
                     + ("正收益+2" if c["ret"] > 0 else ""))
            bonus = f"（{bonus}）" if bonus else ""
            lines.append(f"- {CLAN_CN[c['clan']]}：收益{c['ret'] * 100:+.1f}%｜"
                         f"超额{c['excess'] * 100:+.1f}pp｜夏普{c['sharpe']:.2f}｜"
                         f"回撤{c['maxdd'] * 100:.0f}%｜{c['n_trades']}笔｜"
                         f"胜率{c['win_rate'] * 100:.0f}% → 名次分+{c['pts']}{bonus}")
        nf = round_log.get("null_fit") or []
        if nf:
            ne = round_log.get("null_excess") or [0.0] * len(nf)
            lines.append(f"- 零假设基线：6条随机基因 fitness "
                         f"mean {np.mean(nf):.2f}/max {max(nf):.2f}｜超额 "
                         f"mean {np.mean(ne) * 100:+.1f}pp/max {max(ne) * 100:+.1f}pp"
                         f"——门派成绩须显著高于此才非窗口噪声")
        lf = ("-" if round_log["live_fit"] <= -1e17
              else f"{round_log['live_fit']:.2f}")
        pe = round_log.get("paper_excess")
        if pe is None:
            seat_txt = f"｜实盘尚无成交，夺权门槛{round_log.get('seat_margin', SEAT_BASE):+.2f}"
        else:
            seat_txt = (f"｜现役实盘超额{pe * 100:+.1f}%"
                        f"→夺权门槛{round_log['seat_margin']:+.2f}（实盘成绩加权）")
        lines.append(f"- **本轮冠军：{CLAN_CN[round_log['winner']]}**｜席位战：榜首"
                     f"{CLAN_CN.get(round_log.get('leader'), '?')}复赛 "
                     f"{round_log['champ_fit']:.2f} vs 现役 {lf} → "
                     f"{'易主' if round_log.get('took_seat') else '卫冕'}{seat_txt}")
        if round_log.get("insight"):
            lines.append(f"- 洞察：{round_log['insight']}")
    lines.append("\n## 机制迭代（每轮总结驱动）\n")
    cov = meta.get("regime_cov", {})
    lines.append("- 赛程：34年池随机抽窗，按市道覆盖缺口加权（各轮同窗对战，公平不变）——"
                 + "，".join(f"{REG_CN.get(k, k)}{v}轮" for k, v in cov.items()))
    lines.append("- 记忆：各派保留跨轮Top3基因作下轮GA种子（五派同额=公平），每轮盲测重新验证")
    cr = meta.get("clan_regime", {})
    if cr:
        lines.append("\n| 市道各派战绩(跑赢基准) | "
                     + " | ".join(CLAN_CN[n] for n in CLANS) + " |")
        lines.append("|" + "---|" * (len(CLANS) + 1))
        for rn in RG.NAMES:
            cells = [REG_CN.get(rn, rn)]
            for cn in CLANS:
                s = cr.get(cn, {}).get(rn)
                cells.append(f"{s['wins']}/{s['rounds']}" if s else "-")
            lines.append("| " + " | ".join(cells) + " |")
    chgs = [s for s in meta.get("seat_log", []) if s.get("change")]
    if chgs:
        lines.append("\n- 席位史：" + "；".join(
            f"第{s['round']}轮{CLAN_CN.get(s['holder'], s['holder'])}夺位(fit {s['fit']:.2f})"
            for s in chgs[-5:]))
    lines.append("\n规则：每轮同一随机历史窗口，五派同额预算进化后盲测其后60日；"
                 "积分=跑赢基准+3·正收益+2·名次分(5~1)；实盘席位=榜首冠军须在最新480日窗"
                 "复赛**超过现役+夺权门槛**才夺权，门槛=0.05+0.10×现役自上岗实盘超额"
                 "（实盘成绩加权，防噪声换岗），且须过随机窗资格赛（防最新窗专才）。"
                 "完整轮次档案=results/league_rounds.jsonl；反作弊审计=anti_cheat.py。\n")
    out = C.RESULTS_DIR / "latest" / "league.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def league_round(pop=16, gens=2, n_proc=None, budget_minutes=8.0):
    """门派联赛一轮：同一随机历史窗口，五派同预算进化→同窗盲测→积分。
    Fairness: same window, same costs, same GA budget for every clan.
    实盘席位: 榜首冠军 vs 现役 live 在最新窗口复赛，胜者上岗。
    Co-load aware: WF validation running (full_run.pid alive) or tight RAM ->
    equal-budget (8,1) mode so a full round ALWAYS completes inside the
    9-minute watchdog, even while sharing the machine."""
    free_gb = _free_ram_gb()
    co = (C.RESULTS_DIR / "full_run.pid").exists() or free_gb < 2.5
    if co and pop > 8:
        pop, gens = 8, 1  # same for every clan: fairness preserved
    cache = D.load_cache()
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    league = _load_league()
    meta = _load_meta(league)
    live = _load_live()
    rng = np.random.default_rng(int(time.time() * 1000) & 0xFFFFFF)
    i0, i1, j1, win_reg = _pick_window(cache, reg, meta, rng)
    bench = np.asarray(cache["bench_csi500"][i1:j1], dtype=np.float64)
    if not np.isfinite(bench[0]) or bench[0] <= 0:
        # CSI500 is only published since 2007-01-15: pre-2007 rounds score
        # against the SSE composite instead - a REAL benchmark, no free wins.
        bench = np.asarray(cache["bench_sse"][i1:j1], dtype=np.float64)
        bench_src = "sse"
    else:
        bench_src = "csi500"
    bret = float(bench[-1] / bench[0] - 1) if bench[0] > 0 else 0.0
    t0 = time.time()
    round_no = int(meta.get("n_valid", 0)) + 1
    round_log = {"round": round_no,
                 "window": [str(cache["dates"][i1]), str(cache["dates"][j1 - 1])],
                 "regime": RG.NAMES[win_reg], "bench_ret": round(bret, 4),
                 "bench_src": bench_src,
                 "pop": pop, "gens": gens, "co_load": bool(co),
                 "clans": []}
    ev = Evaluator(n_proc)
    try:
        fought = []
        for name, spec in CLANS.items():
            if time.time() - t0 > budget_minutes * 60 * 0.75 and fought:
                print(f"  [league] budget stop before {name}", flush=True)
                break  # fairness: either all clans fight or none count
            print(f"  [league] {name} fighting (pop={pop},gens={gens})...",
                  flush=True)
            mask = _clan_mask(spec)
            st = league[name]
            # 门派记忆迭代: cross-round top-3 genomes seed this round's GA
            seed = ([row["g"] for row in st.get("mem", [])[:3]]
                    or ([st["champ"]] if st.get("champ") else None))
            best_g, _, _, _ = run_ga(ev, i0, i1, pop=pop, gens=gens,
                                      seed=int(rng.integers(1 << 30)),
                                      init=seed, mask=mask)
            gp = decode(best_g, fam_mask=mask)
            fams = S.family_signals(D.window(cache, i1 - 1, j1 - 1),
                                    gp["params"])
            res = BT.simulate(D.window(cache, i1, j1), fams, gp, reg, i1)
            m = res["metrics"]
            excess = m["total"] - bret
            score = BT.fitness(m)
            # pending per-clan state - applied ONLY if the round counts:
            # a budget-voided round must not advance ANY clan (fairness;
            # otherwise dict-order-favored clans farm stats for free).
            g_list = np.asarray(best_g).tolist()
            mem = [dict(row) for row in st.get("mem", [])]
            mem.append({"g": g_list, "score": round(float(score), 4),
                        "ret": round(m["total"], 4),
                        "window": [str(cache["dates"][i1]),
                                   str(cache["dates"][j1 - 1])]})
            mem.sort(key=lambda r: -r["score"])
            mem = mem[:3]  # every clan keeps the same top-K: fairness preserved
            champ, champ_sc = st.get("champ"), st.get("champ_score", -1e18)
            if champ is None or score >= champ_sc:
                champ, champ_sc = g_list, round(float(score), 4)
            bv, bvr, bvw = (st["best_val"], st["best_val_ret"],
                            st["best_val_window"])
            if score > bv:
                bv, bvr = round(float(score), 4), round(m["total"], 4)
                bvw = [str(cache["dates"][i1]), str(cache["dates"][j1 - 1])]
            fought.append({"clan": name, "excess": round(excess, 4),
                           "ret": round(m["total"], 4),
                           "sharpe": round(float(m["sharpe"]), 2),
                           "maxdd": round(float(m["maxdd"]), 4),
                           "n_trades": int(m["n_trades"]),
                           "win_rate": round(float(m["win_rate"]), 3),
                           "win": int(excess > 0),
                           "new": {"mem": mem, "champ": champ,
                                   "champ_score": champ_sc, "best_val": bv,
                                   "best_val_ret": bvr,
                                   "best_val_window": bvw}})
        if len(fought) < len(CLANS):
            # budget hit before all clans fought: round invalid (fairness rule)
            _save_league(league, meta)
            return {"league": league, "rounds": 0, "valid": False,
                    "cache": cache, "regime": reg,
                    "out_dir": C.RESULTS_DIR / "latest"}
        # round counts: apply ALL pending clan states at once (see above)
        for c in fought:
            st = league[c["clan"]]
            st["rounds"] += 1
            st["sum_excess"] += c["excess"]
            st["sum_ret"] += c["ret"]
            st["wins"] += c["win"]
            st.update(c["new"])
        # rank points by excess (5..1)
        for rk, c in enumerate(sorted(fought, key=lambda x: -x["excess"])):
            pts = len(CLANS) - rk
            league[c["clan"]]["pts"] += pts
            c["pts"] = pts
            if c["excess"] > 0:
                league[c["clan"]]["pts"] += 3
            if c["ret"] > 0:
                league[c["clan"]]["pts"] += 2
        winner = max(fought, key=lambda x: x["excess"])["clan"]
        lean = [{k: c[k] for k in ("clan", "excess", "ret", "sharpe", "maxdd",
                                   "n_trades", "win_rate", "pts")}
                for c in fought]  # keep genomes out of round_log archives
        round_log["clans"] = lean
        round_log["winner"] = winner
        # 零假设基线（科学审计#1）：同窗随机基因组分布——门派冠军的超额/
        # 得分只有显著高于此分布才不是窗口噪声，冠军主张从此可证伪
        null_fit, null_ex = [], []
        for _ in range(6):
            gp_n = decode(rng.random(D_GENOME))
            w_any = np.asarray(gp_n["w"]).max(axis=0) > 1e-4
            fams_n = S.family_signals(
                D.window(cache, i1 - 1, j1 - 1), gp_n["params"],
                fams=[f for f, k in zip(S.FAMILIES, w_any) if k])
            m_n = BT.simulate(D.window(cache, i1, j1), fams_n, gp_n,
                              reg, i1)["metrics"]
            null_fit.append(round(float(BT.fitness(m_n)), 4))
            null_ex.append(round(float(m_n["total"]) - bret, 4))
        round_log["null_fit"] = null_fit
        round_log["null_excess"] = null_ex
        # 实盘席位挑战赛: 榜首冠军 vs 现役 live, 最新480日窗复赛
        leader = max(league.items(), key=lambda kv: kv[1]["pts"])[0]
        champ_g = np.asarray(league[leader]["champ"], dtype=np.float32)
        outs = ev.map([(np.asarray(g, dtype=np.float32),
                        T - C.TRAIN_DAYS, T, False, None)
                       for g in [champ_g] +
                       ([np.asarray(live["genome"], dtype=np.float32)]
                        if live and live.get("genome") else [])])
        champ_fit = float(outs[0][0])
        live_fit = float(outs[1][0]) if len(outs) > 1 else -1e18
        # 实盘成绩加权: incumbent's REAL paper excess sets the challenger bar
        paper_excess, paper_base = _paper_excess_since(cache, live)
        if paper_excess is None:
            seat_margin = SEAT_BASE
        else:
            seat_margin = min(max(SEAT_BASE + SEAT_LIVE_W * paper_excess,
                                  SEAT_MARGIN_LO), SEAT_MARGIN_HI)
        took_seat = champ_fit > live_fit + seat_margin
        # 反作弊资格赛 (user order 2026-09-21 防AI作弊): a challenger that
        # merely overfits the LATEST window must also hold up on RANDOM
        # windows before it may take the live seat. Symmetric windows for
        # both genomes = fair; denial keeps the incumbent accumulating its
        # live record instead of seat-flipping to a specialist genome.
        qual_note = None
        if took_seat and live and live.get("genome"):
            rng_q = np.random.default_rng(
                (int(time.time() * 1000) ^ (round_no << 8)) & 0xFFFFFF)
            hi_q = max(C.START_OFFSET + 1, T - 60)
            ws = sorted({int(rng_q.integers(C.START_OFFSET, hi_q))
                         for _ in range(9)})[:6]
            if len(ws) >= 4:
                jobs = []
                for w0 in ws:
                    jobs.append((champ_g, w0, w0 + 60, False, None))
                    jobs.append((np.asarray(live["genome"], dtype=np.float32),
                                 w0, w0 + 60, False, None))
                outq = ev.map(jobs)
                c_avg = float(np.mean([outq[2 * m][0] for m in range(len(ws))]))
                l_avg = float(np.mean([outq[2 * m + 1][0] for m in range(len(ws))]))
                if c_avg < l_avg - 1e-4:
                    took_seat = False
                    qual_note = (f"夺权被拒：随机{len(ws)}窗资格赛 "
                                 f"champ {c_avg:.2f} < 现役 {l_avg:.2f}（最新窗专才）")
                else:
                    qual_note = (f"资格赛过：随机{len(ws)}窗 champ {c_avg:.2f} "
                                 f"≥ 现役 {l_avg:.2f}")
        seat_g = champ_g if took_seat else (np.asarray(live["genome"],
                                                        dtype=np.float32)
                                             if live and live.get("genome")
                                             else champ_g)
        seat_g = np.asarray(_remap_any(seat_g), dtype=np.float32)
    finally:
        ev.close()
    gp = decode(seat_g)
    seat_today = str(np.asarray(cache["dates"])[-1])
    new_live = {"genome": np.asarray(seat_g).tolist(),
                "params": {f: dict(gp["params"][f]) for f in FAMS},
                "w": np.asarray(gp["w"]).tolist(),
                "exposure": np.asarray(gp["exposure"]).tolist(),
                "K": int(gp["K"]), "stop": gp["stop"], "trail": gp["trail"],
                "hold": int(gp["hold"]),
                "trained_through": seat_today,
                "fit": round(champ_fit if took_seat else live_fit, 4),
                "clan": leader if took_seat else (live.get("clan") or "allround"),
                # 上岗日 (kept on defense so live-excess scoring stays honest)
                "seat_date": seat_today if took_seat
                else (live.get("seat_date") or seat_today),
                "paper_excess": paper_excess,
                "seat_margin": round(float(seat_margin), 4)}
    with open(C.RESULTS_DIR / "live_genome.json", "w", encoding="utf-8") as f:
        json.dump(new_live, f, ensure_ascii=False, indent=2)
    # ---- 每轮总结 + 机制迭代 bookkeeping ----
    rn = RG.NAMES[win_reg]
    meta["n_valid"] = round_no
    meta["regime_cov"][rn] = int(meta["regime_cov"].get(rn, 0)) + 1
    for c in fought:
        s = (meta["clan_regime"].setdefault(c["clan"], {})
             .setdefault(rn, {"rounds": 0, "wins": 0, "sum_excess": 0.0}))
        s["rounds"] += 1
        s["wins"] += 1 if c["excess"] > 0 else 0
        s["sum_excess"] = round(s["sum_excess"] + c["excess"], 4)
    seat_row = {"round": round_no, "holder": new_live["clan"],
                "fit": new_live["fit"], "change": bool(took_seat)}
    meta["seat_log"].append(seat_row)
    del meta["seat_log"][:-50]
    wrow = meta["clan_regime"].get(winner, {}).get(rn, {})
    insight = (f"{CLAN_CN[winner]}在{REG_CN[rn]}市道窗口夺冠；该派跨轮跑赢基准"
                f"战绩{wrow['wins']}/{wrow['rounds']}")
    if took_seat:
        insight += f"；{CLAN_CN[leader]}夺下实盘席位"
    if qual_note:
        insight += f"；{qual_note}"
    round_log["leader"] = leader
    round_log["champ_fit"] = round(champ_fit, 4)
    round_log["live_fit"] = round(live_fit, 4)
    round_log["took_seat"] = bool(took_seat)
    round_log["paper_excess"] = paper_excess
    round_log["seat_margin"] = round(float(seat_margin), 4)
    if qual_note:
        round_log["qual"] = qual_note
    round_log["insight"] = insight
    meta["recent"].append({"round": round_no, "window": round_log["window"],
                            "regime": rn, "bench_ret": round(bret, 4),
                            "bench_src": bench_src,
                            "winner": winner,
                            "win_excess": max(c["excess"] for c in fought),
                            "seat_change": bool(took_seat),
                            "seat_holder": new_live["clan"]})
    del meta["recent"][:-12]
    with open(_rounds_path(), "a", encoding="utf-8") as f:  # 永久轮次档案
        f.write(json.dumps({**round_log,
                            "time": time.strftime("%Y-%m-%d %H:%M"),
                            "seat": seat_row,
                            "standings": {n: league[n]["pts"] for n in CLANS}},
                           ensure_ascii=False) + "\n")
    _save_league(league, meta, round_log)
    return {"league": league, "rounds": len(fought), "valid": True,
            "round": round_no, "regime_name": rn,
            "winner": winner, "leader": leader, "took_seat": took_seat,
            "champ_fit": round(champ_fit, 4), "live_fit": round(live_fit, 4),
            "round_log": round_log, "cache": cache, "regime": reg,
            "live": new_live, "out_dir": C.RESULTS_DIR / "latest"}


def deepen(gens=5, pop=None, n_proc=None):
    """Fast self-evolution step (10-min cadence): GA generations on the LATEST
    window, seeded from the current live genome. Pure evolution deepening for
    closed-market hours; refreshes results/live_genome.json."""
    pop = pop or 32
    cache = D.load_cache()
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    live = _load_live()
    seed = [live["genome"]] if live else None

    ev = Evaluator(n_proc)
    try:
        best_g, best_f, _, hist = run_ga(ev, max(0, T - C.TRAIN_DAYS), T,
                                          pop=pop, gens=gens,
                                          seed=int(time.time()) & 0xFFFF,
                                          init=seed)
    finally:
        ev.close()
    gp = decode(best_g)
    live = {"genome": np.asarray(best_g).tolist(),
            "params": {f: dict(gp["params"][f]) for f in FAMS},
            "w": np.asarray(gp["w"]).tolist(),
            "exposure": np.asarray(gp["exposure"]).tolist(),
            "K": int(gp["K"]), "stop": gp["stop"], "trail": gp["trail"],
            "hold": int(gp["hold"]),
            "trained_through": str(np.asarray(cache["dates"])[-1]),
            "fit": round(float(best_f), 4), "gens": len(hist)}
    with open(C.RESULTS_DIR / "live_genome.json", "w", encoding="utf-8") as f:
        json.dump(live, f, ensure_ascii=False, indent=2)
    return {"live": live, "cache": cache, "regime": reg,
            "out_dir": C.RESULTS_DIR / "latest",
            "fit": float(best_f), "hist": hist}


if __name__ == "__main__":
    import sys
    tag = sys.argv[1] if len(sys.argv) > 1 else "wf"
    r = run_walkforward(tag=tag)
    print("done:", r["summary"])
