# -*- coding: utf-8 -*-
"""r326 bm-c T-134 s2 SIXTH-conversion real-path pool==serial identity smoke
for scripts/cn_rev_tilt_p1.py (r324 p4b3 smoke precedent).

Real panel + real signal/selection construction + real unit bodies; tilt
cells get the REAL trail weight map (computed from the serial bare/mom
x1 results with the runner's own formula). Checkpoints bypassed (units
computed fresh on both paths, tmp only); zero repo products, no ledger,
no prereg touch (r312 zero-repo-products law; spawn __main__ guard law).

Evidence -> results/_r326bmc_revtilt_pool_smoke.json
"""
import json
import os
import sys
import tempfile
import time

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, BM)
sys.path.insert(0, os.path.join(BM, "scripts"))
sys.path.insert(0, os.path.join(BM, "screening"))

import numpy as np
import pandas as pd


def _req(a, b):
    if set(a) != set(b):
        return False
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, pd.Series):
            if not va.equals(vb):
                return False
        elif va != vb:
            return False
    return True


def main() -> int:
    import cn_rev_tilt_p1 as rt
    from parallel_runner import run_cells_parallel
    from alloc_backtest import V1_FLAT_SIDE

    t0 = time.time()
    panel_face = "P1C census close (primary, runner load_panel)"
    try:
        close = rt.load_panel()
    except FileNotFoundError:
        # r316 data-face law: P1C cache (Money02\data\cache\p1c_stock) is
        # machine-local and absent on bm-c -- honest fallback to the REAL
        # core48 daily panel (data\daily\*.csv, same close-only face),
        # disclosed in the evidence JSON. Identity proof is panel-agnostic
        # (it proves the pool plumbing vs serial on the real unit body).
        panel_face = ("data\\daily real-panel fallback, 1724 syms "
                      "(P1C census cache absent on bm-c -- r316 "
                      "data-face law, host=bm-a/bm-b)")
        daily = os.path.join(BM, "data", "daily")
        frames = {}
        for fn in sorted(os.listdir(daily)):
            if not fn.endswith(".csv"):
                continue
            code = fn[:-4]
            df = pd.read_csv(os.path.join(daily, fn),
                             usecols=["date", "close"], index_col="date")
            frames[code] = df["close"]
        close = pd.DataFrame(frames)
        close.index = pd.to_datetime(close.index)
        close = close.sort_index().ffill()
        # TRAIL_WIN needs room for a nonzero warmup tail; keep the window
        close = close.tail(max(1400, rt.TRAIL_WIN * 3))
    idx = close.index
    print(f"[smoke] panel: T={len(idx)} N={close.shape[1]} "
          f"cutoff={idx[-1].date()} face={panel_face}", flush=True)
    close_arr = close.to_numpy(dtype=np.float64)
    T = close_arr.shape[0]
    sched = rt.rebal_schedule(T)

    sigs, valids, sels = {}, {}, {}
    for w in rt.W_SET:
        sigs[("rev", w)] = rt.sig_matrix(close_arr, w, "rev")
        sigs[("mom", w)] = rt.sig_matrix(close_arr, w, "mom")
        valids[w] = rt.signal_valid(close_arr, w)
        sels[("rev", w)] = rt.topk_selections(sigs[("rev", w)], valids[w],
                                              sched)
        sels[("mom", w)] = rt.topk_selections(sigs[("mom", w)], valids[w],
                                              sched)

    # -- serial pass: all units computed fresh in-parent (globals route)
    rt._MP_CLOSE = close_arr
    rt._MP_IDX = idx

    def unit_specs(tilt_w_by_w):
        sp = []
        for w in rt.W_SET:
            for face, mult in rt.FACES.items():
                sp.append((f"cell_REV{w}_bare_{face}", sels[("rev", w)],
                           V1_FLAT_SIDE * mult, None))
        for w in rt.W_SET:
            sp.append((f"mach_mom{w}_x1", sels[("mom", w)],
                       V1_FLAT_SIDE, None))
        ew_sels = []
        for r in sched:
            cols = np.flatnonzero(np.isfinite(close_arr[r]))
            ew_sels.append((r, cols if cols.size else None))
        sp.append(("baseline_census_ew", ew_sels, V1_FLAT_SIDE, None))
        for k in range(rt.K_NULLS):
            ns = rt.null_selections(valids[20], sched, rt.SEED_BASE + k)
            sp.append((f"null_{k:02d}", ns, V1_FLAT_SIDE, None))
        if tilt_w_by_w is not None:
            for w in rt.W_SET:
                for face, mult in rt.FACES.items():
                    sp.append((f"cell_REV{w}_tilt_{face}", sels[("rev", w)],
                               V1_FLAT_SIDE * mult, tilt_w_by_w[w]))
        return sp

    t1 = time.time()
    b1_specs = unit_specs(None)
    ser1 = {}
    for i, (u, s, rate, wbr) in enumerate(b1_specs):
        ser1[u] = rt._unit_body(u, s, rate, wbr)
        if (i + 1) % 10 == 0:
            print(f"  [serial] {i + 1}/{len(b1_specs)}", flush=True)

    # -- REAL trail weight map from the serial bare/mom x1 results
    #    (verbatim formula from run(); frozen constants via rt.*)
    tilt_w_by_w = {}
    for w in rt.W_SET:
        rv = ser1[f"cell_REV{w}_bare_x1"]["returns"].fillna(0.0)
        mm = ser1[f"mach_mom{w}_x1"]["returns"].fillna(0.0)
        cum_r = (1.0 + rv).cumprod().to_numpy()
        cum_m = (1.0 + mm).cumprod().to_numpy()
        e0 = ser1[f"cell_REV{w}_bare_x1"]["first_entry_day"]
        pos = np.arange(T)
        win_ok = (pos >= (e0 + rt.TRAIL_WIN)) if e0 is not None \
            else np.zeros(T, dtype=bool)
        cr = cum_r / np.concatenate(
            [np.full(rt.TRAIL_WIN, np.nan), cum_r[:-rt.TRAIL_WIN]])
        cm = cum_m / np.concatenate(
            [np.full(rt.TRAIL_WIN, np.nan), cum_m[:-rt.TRAIL_WIN]])
        tv_all = cr - cm
        tv_all[~win_ok] = np.nan
        tw = {}
        for r in sched:
            tv = tv_all[r]
            tw[r] = 0.0 if not np.isfinite(tv) else \
                (rt.TILT_HI if tv > 0 else rt.TILT_LO)
        tilt_w_by_w[w] = tw
    t2_specs = [(f"cell_REV{w}_tilt_{face}", sels[("rev", w)],
                 V1_FLAT_SIDE * mult, tilt_w_by_w[w])
                for w in rt.W_SET for face, mult in rt.FACES.items()]
    ser2 = {}
    for i, (u, s, rate, wbr) in enumerate(t2_specs):
        ser2[u] = rt._unit_body(u, s, rate, wbr)
    t_serial = time.time() - t1
    print(f"[smoke] serial pass done: {len(ser1) + len(ser2)} units "
          f"in {t_serial:.1f}s", flush=True)

    # -- pool pass: batch-1 (59) then batch-2 (6), payload-aware cap
    nw = rt._pool_worker_cap(close_arr)
    t2 = time.time()
    jobs1 = [(u, rt._mp_job, (u, s, rate, wbr))
             for (u, s, rate, wbr) in b1_specs]
    pool1 = run_cells_parallel(jobs1, workers=nw, desc="smoke-b1",
                               initializer=rt._mp_init,
                               initargs=(close_arr, idx))
    w1 = pool1.pop("__workers__")
    jobs2 = [(u, rt._mp_job, (u, s, rate, wbr))
             for (u, s, rate, wbr) in t2_specs]
    pool2 = run_cells_parallel(jobs2, workers=nw, desc="smoke-b2",
                               initializer=rt._mp_init,
                               initargs=(close_arr, idx))
    w2 = pool2.pop("__workers__")
    t_pool = time.time() - t2

    ident1 = all(_req(pool1[u], ser1[u]) for u in ser1)
    ident2 = all(_req(pool2[u], ser2[u]) for u in ser2)
    n_units = len(ser1) + len(ser2)
    evidence = {
        "round": "r326 bm-c",
        "ticket": "T-2026-10-01-134 s2 (T-134 s2 sixth conversion)",
        "runner": "scripts/cn_rev_tilt_p1.py",
        "smoke": "real-path pool==serial identity (r324 p4b3 precedent)",
        "panel": {"T": int(len(idx)), "N": int(close.shape[1]),
                  "cutoff": str(idx[-1].date()),
                  "face": panel_face,
                  "panel_mb": round(close_arr.nbytes / 1024 ** 2, 1)},
        "units": {"batch1": len(ser1), "batch2": len(ser2),
                  "total": n_units},
        "workers": {"batch1": w1, "batch2": w2, "cap_requested": nw},
        "elapsed_sec": {"serial": round(t_serial, 1),
                        "pool": round(t_pool, 1),
                        "total": round(time.time() - t0, 1)},
        "identity": {"batch1_all_identical": bool(ident1),
                     "batch2_all_identical": bool(ident2),
                     "verdict": "PASS" if (ident1 and ident2) else "FAIL"},
        "tilt_weights": "REAL trail map from serial bare/mom x1 results "
                        "(runner formula verbatim)",
        "ckpt": "bypassed (fresh compute both paths, tmp only)",
        "zero_repo_products": True,
    }
    out = os.path.join(BM, "results", "_r326bmc_revtilt_pool_smoke.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1)
    print(f"[smoke] identity batch1={ident1} batch2={ident2} "
          f"units={n_units} workers={w1}/{w2} "
          f"serial={t_serial:.1f}s pool={t_pool:.1f}s", flush=True)
    print(f"[smoke] evidence -> {out}", flush=True)
    return 0 if (ident1 and ident2) else 1


if __name__ == "__main__":
    sys.exit(main())
