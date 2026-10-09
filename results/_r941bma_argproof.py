# r941 arg-plumbing proof for the retrofitted _cell_compute (synthetic fixture,
# no panel load): proves the ProcessPool path end-to-end with the exact jobs
# tuple shape used in cmd_run. This is NOT the burn -- the watchdog owns that.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) or '.')

import numpy as np


def main():
    import thermo_overlay_p1 as M
    from parallel_runner import run_cells_parallel, worker_cap
    rng = np.random.default_rng(42)
    T = 300
    r_u = rng.normal(0.0003, 0.01, T)
    years = np.array([2000 + (i // 50) for i in range(T)])
    shifts = [int(np.random.default_rng(94500 + i).integers(1, T)) for i in range(40)]
    masks = {
        "SYN_A": np.zeros(T, dtype=bool),
        "SYN_B": (rng.random(T) > 0.9),
    }
    passive_sr = 0.35
    passive_sum = float(r_u.sum())

    jobs = [(name, M._cell_compute,
             (name, np.asarray(r_u, dtype=float), np.asarray(off, dtype=bool),
              years, shifts, passive_sr, passive_sum))
            for name, off in masks.items()]
    par = run_cells_parallel(jobs, workers=min(len(jobs), worker_cap()),
                             desc="synthetic cells")
    w = par.pop("__workers__", 1)
    for name in masks:
        res = par[name]
        assert res["segs"] == M.count_segments(masks[name]), name
        assert len(res["x1"]) == T, name
        assert len(res["null_rows"]) == len(shifts), name
        assert res["null_cov_raw"] is not None and res["null_cov_raw"]["n_values"] >= 30, name
        x1 = np.asarray(res["x1"])
        # serial oracle: identical math outside the pool
        x1s = M.overlay_stream(r_u, masks[name], M.COST_SIDE_X1)
        assert np.array_equal(x1, x1s), f"pool/serial drift {name}"
        srs = res["null_rows"][0]
        nmr = np.asarray(masks[name], dtype=bool)[(np.arange(T) + shifts[0]) % T]
        assert srs[4] == M._sharpe(M.overlay_stream(r_u, nmr, M.COST_SIDE_X1)), name
    print("ARG-PLUMBING PROOF PASS: workers=%d cells=%d nulls/cell=%d pool==serial byte-identical" % (w, len(masks), len(shifts)))


if __name__ == "__main__":
    main()
