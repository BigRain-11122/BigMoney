"""Instrumented league round (guarded)."""
import time

t0 = time.time()


def main():
    import evolve as EV
    import numpy as np

    free = EV._free_ram_gb()
    print(f"[{time.time()-t0:.0f}s] freeRAM={free:.1f}GB", flush=True)

    ev = EV.Evaluator()
    print(f"[{time.time()-t0:.0f}s] evaluator n_proc={ev.n_proc}", flush=True)

    t1 = time.time()
    out = ev.map([(np.random.rand(EV.D_GENOME).astype(np.float32),
                   610, 1090, False, None) for _ in range(16)])
    per = (time.time() - t1) / 16
    print(f"[16 evals in {time.time()-t1:.0f}s => {per:.1f}s/eval "
          f"x {ev.n_proc} workers]", flush=True)
    ev.close()

    t1 = time.time()
    res = EV.league_round()
    print(f"[league_round {time.time()-t1:.0f}s valid={res.get('valid')} "
          f"winner={res.get('winner')}]", flush=True)


if __name__ == "__main__":
    main()
