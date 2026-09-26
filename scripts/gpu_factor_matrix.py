"""GPU factor-matrix lane first batch (O-20260926-0947 s3, T-77 slice-4).

PLAN.md s1.3 GPU-delegated class: ">100-factor library matrix work -> GPU
(torch), batched Z-score + IC matrix". This runner establishes the LANE
with a first engineering-proof batch over the frozen P1E census factor
faces (7 members x 3 horizons = 21 faces, p1e_factors frozen constructors
reused verbatim -- zero rewrite):

  * torch-batched masked cross-sectional z-score + average-tie rank IC
    (Spearman) over the full-instrument census panel, all faces batched
    per horizon into one (K, T, N) device tensor;
  * per-face equivalence vs the established CPU fast-IC reference
    (shortline_p1_ic._ic_series_fast, the p1e batch-pre gate lineage):
    max|d| <= 1e-6 required on EVERY face (NaN-day pattern must match
    exactly), fail-closed exit 2;
  * honest engineering scope: NO science gates, NO ledger append, NO
    registration -- proof.json is an infrastructure artifact, never a
    science face (any downstream consumption needs its own prereg).

Mask semantics mirror the pandas reference exactly: NaN excluded from
ranks/stats (torch.sort places NaN last; NaN != NaN keeps each sentinel
its own tie group, so data +-inf forms its own group, pandas-style),
+-inf ranked as a value (pandas notna() keeps inf).

Physical dependency (ticket T-77 slice-4): torch+CUDA host required --
bm-a-box GPU lane. On a host without torch/CUDA the runner refuses to
run (exit 2, honest) and selftest reports the torch leg as SKIP (never
FAIL: the numpy reference machinery is fully testable everywhere; the
bm-a-side flip gate = selftest with torch leg PASS + first run green).

Exit codes: 0 = proof landed | 2 = torch/CUDA absent, cache missing,
or equivalence FAIL (fail-closed, zero artifacts).
selftest = hermetic offline (numpy reference vs hand-computed; torch
core vs numpy reference when torch importable). No network, no cache.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT_DIR = os.path.join(ROOT, "results", "gpu_factor_lane")
PROOF_JSON = os.path.join(OUT_DIR, "proof.json")
HORIZONS = [5, 10, 20]
EQUIV_TOL = 1e-6          # p1e batch-pre gate lineage threshold
EQUIV_TOL_CORE = 1e-9     # selftest torch-vs-numpy core (float64)
SPOT_SLICE = (200, 60)    # z-score spot-check slice (rows, cols)
MIN_NAMES = 5             # reference IC convention: < 5 valid names -> NaN


# ------------------------------------------------- numpy reference (always)

def _avg_rank_rows_np(x, valid):
    """Reference: per-row average-tie ranks over the valid intersection
    (pandas rank(method='average') semantics, 1-based). Invalid -> NaN."""
    out = np.full(x.shape, np.nan)
    for t in range(x.shape[0]):
        v = valid[t]
        if not v.any():
            continue
        vals = x[t][v]
        order = np.argsort(vals, kind="stable")
        sv = vals[order]
        ranks = np.empty(len(vals))
        i = 0
        while i < len(sv):
            j = i
            while j + 1 < len(sv) and sv[j + 1] == sv[i]:
                j += 1
            ranks[i:j + 1] = 0.5 * (i + j) + 1.0     # 1-based average
            i = j + 1
        out[t][v] = ranks[np.argsort(order, kind="stable")]
    return out


def _masked_zscore_np(x, valid):
    """Reference masked per-row z-score (population sd, ddof=0 -- declared
    convention for the lane). Rows with no valid entries -> NaN row."""
    out = np.full(x.shape, np.nan)
    for t in range(x.shape[0]):
        v = valid[t]
        n = int(v.sum())
        if n == 0:
            continue
        vals = x[t][v]
        mu = vals.mean()
        sd = vals.std()                     # ddof=0
        out[t][v] = (vals - mu) / sd if sd > 0 else 0.0
    return out


def _masked_rank_ic_np(x, y, valid):
    """Reference: per-row Pearson corr of average ranks = Spearman IC,
    pairwise-complete mask, zero-variance -> NaN, n < 5 -> NaN."""
    fr = _avg_rank_rows_np(x, valid)
    rr = _avg_rank_rows_np(y, valid)
    out = np.full(x.shape[0], np.nan)
    for t in range(x.shape[0]):
        v = valid[t]
        n = int(v.sum())
        if n < MIN_NAMES:
            continue
        a = fr[t][v]
        b = rr[t][v]
        da = a - a.mean()
        db = b - b.mean()
        sa = float(np.sqrt((da ** 2).sum()))
        sb = float(np.sqrt((db ** 2).sum()))
        if sa <= 0 or sb <= 0:
            continue
        out[t] = float((da * db).sum() / (sa * sb))
    return out


# ------------------------------------------------------ torch core (device)

def _import_torch():
    try:
        import torch
    except ImportError as ex:
        raise RuntimeError(
            f"torch absent on this host ({ex}) -- GPU lane host (bm-a-box, "
            f"T-77 slice-4 physical dependency) required; refuse to run") from ex
    if not torch.cuda.is_available():
        raise RuntimeError("torch present but CUDA unavailable -- GPU lane "
                           "host required (refuse CPU fallback: PLAN s1.3 "
                           "class is GPU-delegated by law)")
    return torch


def _t_core(torch):
    """Batched masked average-tie ranks + Pearson + z-score on device.

    Mirrors the numpy reference exactly (validated in selftest). NaN
    stays NaN: torch.sort places it last and NaN != NaN keeps every
    sentinel its own tie group, so a data +-inf group is never mixed
    with sentinels (pandas notna() keeps inf as a rankable value).
    Pearson is shift-invariant, so 0-based ordinals == pandas 1-based
    average ranks for the correlation."""

    def avg_ranks(xs, valid):
        T, N = xs.shape
        sv, si = torch.sort(xs, dim=1)          # NaN sorts last
        pos = torch.arange(N, device=xs.device, dtype=xs.dtype) \
            .unsqueeze(0).expand(T, N)
        diff = torch.cat(
            [torch.ones(T, 1, device=xs.device, dtype=xs.dtype),
             (sv[:, 1:] != sv[:, :-1]).to(xs.dtype)], dim=1)
        gid = diff.cumsum(dim=1) - 1.0
        G = int(gid.max().item()) + 1
        gidl = gid.long()
        cnt = torch.zeros(T, G, device=xs.device, dtype=xs.dtype) \
            .scatter_add_(1, gidl, torch.ones_like(xs))
        ssum = torch.zeros(T, G, device=xs.device, dtype=xs.dtype) \
            .scatter_add_(1, gidl, pos)
        avg_sorted = ssum.gather(1, gidl) / cnt.gather(1, gidl)
        avg = torch.empty_like(avg_sorted)
        avg.scatter_(1, si, avg_sorted)    # back to original column order
        return avg * valid.to(xs.dtype)     # invalid (incl. NaN) -> 0

    def rank_ic(x, y, valid):
        vf = valid.to(x.dtype)
        fr = avg_ranks(x, valid)
        rr = avg_ranks(y, valid)
        n = vf.sum(dim=1)
        fm = (fr * vf).sum(dim=1) / n
        rm = (rr * vf).sum(dim=1) / n
        df_ = (fr - fm.unsqueeze(1)) * vf
        dr_ = (rr - rm.unsqueeze(1)) * vf
        cov = (df_ * dr_).sum(dim=1)
        sf = df_.pow(2).sum(dim=1).sqrt()
        sr = dr_.pow(2).sum(dim=1).sqrt()
        ic = cov / (sf * sr)
        bad = (sf <= 0) | (sr <= 0) | (n < MIN_NAMES)
        return torch.where(bad, torch.full_like(ic, float("nan")), ic)

    def zscore(x, valid):
        xs = torch.where(valid, x, torch.zeros_like(x))  # NaN must not
        vf = valid.to(xs.dtype)                          # propagate into
        n = vf.sum(dim=1, keepdim=True)                  # row stats
        mu = (xs * vf).sum(dim=1, keepdim=True) / n
        d = (xs - mu) * vf
        sd = d.pow(2).sum(dim=1, keepdim=True).div(
            torch.where(n > 0, n, torch.ones_like(n))).sqrt()
        z = torch.where(sd > 0, d / sd, torch.zeros_like(d))
        return z * vf

    return avg_ranks, rank_ic, zscore


# ------------------------------------------------------------------ faces

def _build_faces(panels):
    """Frozen P1E factor faces, constructors reused verbatim (zero
    rewrite; p1e_factors is selftest-gated upstream)."""
    import p1e_factors as F
    close, open_, tr_frac = panels["close"], panels["open"], panels["tr"]
    vwap = panels["vwap"]
    rets = close / close.shift(1) - 1.0
    faces = {}
    faces["zoo85_terrified"] = F.build_zoo85_terrified(rets)
    faces["zoo85_stv"] = F.build_zoo85_stv(rets, tr_frac)
    faces["zoo92_coin_team"] = F.build_zoo92_coin_team(close, open_, tr_frac)
    fam, n_bad = F.build_zoo93_arc_family(tr_frac, vwap, close)
    for nm in ("zoo93_arc", "zoo93_vrc", "zoo93_src", "zoo93_krc"):
        faces[nm] = fam[nm]
    del fam
    return faces, int(n_bad)


def run():
    torch = _import_torch()
    import p1e_ic_batch as P1E
    import p1c_stock_ic_batch as P1C
    from shortline_p1_ic import _ic_series_fast
    t0 = time.time()
    idx, syms, meta, panels = P1E.load_panels({"close", "open", "tr", "vwap"})
    fwd = P1C.fwd_rets({"close": panels["close"]})
    faces, n_bad = _build_faces(panels)
    dev = torch.device("cuda")
    avg_ranks, rank_ic, zscore = _t_core(torch)
    names = list(faces)
    K, T, N = len(names), len(idx), len(syms)
    print(f"census panel T={T} N={N} faces={K} device="
          f"{torch.cuda.get_device_name(0)} torch={torch.__version__}",
          flush=True)

    equiv, timing = {}, {}
    for h in HORIZONS:
        fh = fwd[h]
        # pandas notna() semantics: NaN excluded, +-inf KEPT as a value
        valid_np = ~np.isnan(fh.values)
        y = torch.from_numpy(fh.values).to(dev, torch.float64)
        stack = torch.zeros(K, T, N, device=dev, dtype=torch.float64)
        fvalid = torch.zeros(K, T, N, device=dev, dtype=torch.bool)
        for k, nm in enumerate(names):
            arr = faces[nm].values
            fvalid[k] = torch.from_numpy(~np.isnan(arr) & valid_np).to(dev)
            stack[k] = torch.from_numpy(arr).to(dev, torch.float64)
        torch.cuda.synchronize()
        tg = time.time()
        zs = zscore(stack, fvalid)               # batched z-score product
        ic = torch.stack([rank_ic(stack[k], y, fvalid[k])
                          for k in range(K)])    # (K, T) rank-IC matrix
        torch.cuda.synchronize()
        t_gpu = time.time() - tg

        # z-score spot-check vs numpy reference on a real slice
        r0, c0 = max(T - SPOT_SLICE[0], 0), max(N - SPOT_SLICE[1], 0)
        ref_z = _masked_zscore_np(
            stack[0, r0:, c0:].cpu().numpy(),
            fvalid[0, r0:, c0:].cpu().numpy())
        got_z = zs[0, r0:, c0:].cpu().numpy()
        m = np.isfinite(ref_z)
        z_worst = float(np.abs(ref_z[m] - got_z[m]).max()) if m.any() else 0.0

        # per-face equivalence vs CPU fast-IC reference (fail-closed):
        # NaN-day patterns must match EXACTLY, then max|d| over the rest
        tc = time.time()
        worst_h = 0.0
        for k, nm in enumerate(names):
            ref = _ic_series_fast(faces[nm], fh)
            got = pd.Series(ic[k].cpu().numpy(), index=idx)
            common = ref.index.intersection(got.index)
            rv = ref[common].values
            gv = got[common].values
            if not np.array_equal(np.isnan(rv), np.isnan(gv)):
                d = 9.9                     # NaN-pattern mismatch = fail
            else:
                d = float(np.abs(rv - gv).max()) if len(common) else 9.9
            worst_h = max(worst_h, d)
            equiv[f"{nm}/h{h}"] = {"max_abs_diff": d, "n_days": len(common)}
        t_cpu = time.time() - tc
        timing[f"h{h}"] = {"gpu_batch_s": round(t_gpu, 3),
                           "cpu_reference_s": round(t_cpu, 3),
                           "zscore_spot_worst": z_worst}
        print(f"h{h}: gpu_batch={t_gpu:.2f}s cpu_ref={t_cpu:.2f}s "
              f"equiv max|d|={worst_h:.2e} z_spot={z_worst:.2e}", flush=True)
        if worst_h > EQUIV_TOL or z_worst > EQUIV_TOL:
            print(f"FAIL-CLOSED: h{h} equivalence {worst_h:.2e} / "
                  f"z_spot {z_worst:.2e} > {EQUIV_TOL} -- no artifacts",
                  flush=True)
            return 2
        del stack, fvalid, zs, ic, y
        torch.cuda.empty_cache()

    os.makedirs(OUT_DIR, exist_ok=True)
    proof = {
        "lane": "GPU factor matrix (PLAN s1.3 GPU-delegated class)",
        "order": "O-20260926-0947 s3 / T-77 slice-4 first batch",
        "engineering_lane": True,
        "no_gates_no_ledger_no_registration": True,
        "device": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "faces": names, "horizons": HORIZONS,
        "panel_shape": {"T": T, "N": N},
        "zoo93_nonfinite_arc_cells": n_bad,
        "equiv_tol": EQUIV_TOL,
        "equiv": equiv,
        "timing": timing,
        "elapsed_s": round(time.time() - t0, 1),
        "note": "infrastructure proof only: batched masked z-score + "
                "average-tie rank-IC on GPU vs established CPU fast-IC; "
                "downstream science consumption requires its own prereg; "
                ">100-face production census batches ride this lane",
    }
    with open(PROOF_JSON, "w", encoding="utf-8") as fh:
        json.dump(proof, fh, indent=2, ensure_ascii=False)
    print(f"proof landed: {PROOF_JSON} "
          f"({proof['elapsed_s']}s, all {len(equiv)} faces "
          f"max|d| <= {EQUIV_TOL})", flush=True)
    return 0


# --------------------------------------------------------------- selftest

def selftest():
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("GPU factor-matrix lane selftest:")
    rng = np.random.default_rng(7)
    T, N = 40, 30
    x = rng.standard_normal((T, N))
    y = rng.standard_normal((T, N))
    valid = rng.random((T, N)) < 0.8
    x[0, 6:12] = 1.5                       # 6-way tie group in row 0
    x[:, -1] = np.nan                      # column never valid
    valid &= ~np.isnan(x) & ~np.isnan(y)

    # leg 1: reference z-score vs hand-computed (full row-0 valid set)
    z = _masked_zscore_np(x, valid)
    v = valid[0]
    hand = (x[0][v] - x[0][v].mean()) / x[0][v].std()
    ok("L1 z-score reference vs hand-computed (ddof=0)",
       np.allclose(z[0][v], hand, atol=1e-12)
       and np.all(np.isnan(z[:, -1])))
    # leg 2: reference rank-IC vs hand-computed incl. tie-averaged ranks
    ic = _masked_rank_ic_np(x, y, valid)
    fr = _avg_rank_rows_np(x, valid)[0][v]
    rr = _avg_rank_rows_np(y, valid)[0][v]
    da, db = fr - fr.mean(), rr - rr.mean()
    hand_ic = float((da * db).sum()
                    / np.sqrt((da ** 2).sum() * (db ** 2).sum()))
    ok("L2 rank-IC reference vs hand-computed (tie-averaged)",
       abs(ic[0] - hand_ic) < 1e-12)
    # leg 2b: MIN_NAMES boundary (n=4 -> NaN, n=5 -> finite)
    v4 = np.zeros_like(valid)
    v4[0, 12:16] = True
    v5 = np.zeros_like(valid)
    v5[0, 12:17] = True
    ok("L2b MIN_NAMES=5 boundary (n=4 NaN, n=5 finite)",
       np.isnan(_masked_rank_ic_np(x, y, v4)[0])
       and np.isfinite(_masked_rank_ic_np(x, y, v5)[0]))
    # leg 2c: zero-variance factor row -> NaN
    ok("L2c zero-variance factor row -> NaN",
       np.isnan(_masked_rank_ic_np(np.ones((2, N)), y, valid)).all())
    # leg 3: torch core vs numpy reference (honest SKIP when no torch)
    try:
        torch = _import_torch()
    except RuntimeError as ex:
        print(f"  [SKIP] torch/CUDA core leg (this host): {ex}")
    else:
        avg_ranks, rank_ic, zscore = _t_core(torch)
        dev = torch.device("cuda")
        xt = torch.from_numpy(x).to(dev, torch.float64)
        yt = torch.from_numpy(y).to(dev, torch.float64)
        vt = torch.from_numpy(valid).to(dev)
        ic_t = rank_ic(xt, yt, vt).cpu().numpy()
        ref = _masked_rank_ic_np(x, y, valid)
        m = np.isfinite(ref)
        worst = float(np.abs(ic_t[m] - ref[m]).max()) if m.any() else 9.9
        ok("L3 torch rank-IC vs numpy reference (float64)",
           worst <= EQUIV_TOL_CORE)
        z_t = zscore(xt, vt).cpu().numpy()
        refz = _masked_zscore_np(x, valid)
        mz = np.isfinite(refz)
        wz = float(np.abs(z_t[mz] - refz[mz]).max()) if mz.any() else 9.9
        ok("L3b torch z-score vs numpy reference (float64)",
           wz <= EQUIV_TOL_CORE)
    # leg 4: run-refusal contract (import guard carries the
    # physical-dependency disclosure)
    try:
        _import_torch()
    except RuntimeError as ex:
        ok("L4 run refusal contract (honest physical-dep message)",
           "bm-a-box" in str(ex) or "CUDA" in str(ex))
    else:
        ok("L4 torch+CUDA present on this host (run face live here)",
           True)
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(run())
    except RuntimeError as ex:
        print(f"REFUSED: {ex}", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
