"""_r256bmb_t56old_probe.py -- OLD-CODE (0389dee6) + CURRENT-PANEL discrimination.

Run INSIDE the git worktree checked out at 0389dee6 (T-56 freeze commit)
with the CURRENT data/daily panel copied in. Uses ONLY the old-commit code
(aggressive_lab/t28/live.paper/parallel_runner as of the freeze) to
recompute the two STATIC T-56 variant anchors (AGGR-CONC-TOP2,
AGGR-NOCASH) sleeve-domain w_cur (x1/x2) and compare bit-exactly vs the
worktree-native frozen results/aggressive_lab.json.

Discrimination logic:
  PASS -> current panel is anchor-faithful; the drift lives in the
          post-freeze code/registry face (r241/r242 wiring etc.)
  FAIL -> the data/daily history itself drifted since the T-56 run
Exit: 0 = PASS, 3 = FAIL, 2 = env/gate error
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

STATIC_TWO = ("AGGR-CONC-TOP2", "AGGR-NOCASH")


def main() -> int:
    t0 = time.time()
    import pandas as pd
    import aggressive_lab as al
    from live.paper import load_core
    from parallel_runner import run_cells_parallel, worker_cap
    from t28_stable_profit import (_blend_daily_ret, _sleeve_worker,
                                   _window_face, W_CUR_END, W_CUR_START)

    with open(os.path.join(ROOT, "results", "aggressive_lab.json"),
              encoding="utf-8") as fh:
        frozen = json.load(fh)["variants"]

    faces, sha_checks, _tour = al.build_weights()
    bad = [k for k, v in sha_checks.items() if v != al.FROZEN_SHA[k]]
    if bad:
        print(f"[old-probe] SHA GATE FAIL: {bad}")
        return 2

    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < al.SLEEVE_CUTOFF:
        print(f"[old-probe] PANEL GATE FAIL: {cutoff.date()} < "
              f"{al.SLEEVE_CUTOFF.date()}")
        return 2
    prices = {s: df[df.index <= al.SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    print(f"[old-probe] old-code tree, panel {len(prices)} syms cutoff "
          f"{cutoff.date()} truncated {al.SLEEVE_CUTOFF.date()}")

    jobs = [(tid, mult, prices, al.SLEEVE_CUTOFF) for tid in al.ROSTER
            for mult in (None, 2.0)]
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="old-probe-sleeves")
    sleeves = {}
    for tid in al.ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    print(f"[old-probe] sleeves 28x2 ({time.time()-t0:.0f}s)")

    fails = []
    for name in STATIC_TWO:
        w = faces[name]["static"]
        pr1 = _blend_daily_ret({t: sleeves[t]["x1"] for t in al.ROSTER}, w)
        pr2 = _blend_daily_ret({t: sleeves[t]["x2"] for t in al.ROSTER}, w)
        wcur = {"x1": _window_face(pr1, W_CUR_START, W_CUR_END),
                "x2": _window_face(pr2, W_CUR_START, W_CUR_END)}
        want = frozen[name]["w_cur"]
        ok = wcur == want
        print(f"[old-probe] {name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(name)
            print(f"    got  {json.dumps(wcur)}")
            print(f"    want {json.dumps(want)}")
    print(f"[old-probe] {2 - len(fails)}/2 static anchors reproduced "
          f"({time.time()-t0:.0f}s)")
    return 0 if not fails else 3


if __name__ == "__main__":
    sys.exit(main())
