# r284 bm-a real-data gate probe for CN_SOE_ETF_P1 (pre-pool, r286 law):
# panel gates on the REAL lockbox face + single-cell x2 runs (SOE_HOLD /
# SOE_REPAIR) + json dump-site probe. Zero pool artifacts (no checkpoints,
# no p1_results.json) -- probe only.
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import numpy as np
import cn_soe_etf_p1 as R
from alloc_backtest import side_cost_x2

t0 = time.time()
R.SEED = 20272301                      # registry value (freeze commit)
P, gates = R.load_panel()
if P is None:
    print("PROBE FAIL-CLOSED:", gates)
    sys.exit(2)
T, N = P["T"], P["N"]
print(f"panel: T={T} N={N} syms={P['syms']}")
print(f"gates={P['gates']} sse_cover={P['sse_cover']:.4f}")
print(f"sleeve_start={P['idx'][int(np.argmax(P['n_avail'] > 0))].date()} "
      f"agg_start={P['idx'][P['agg_start']].date()}")
print("avail_starts:", {s: str(P['idx'][t].date())
                        for s, t in zip(P['syms'], P['avail_start'])})
print("duty_cycles(LEGMA200):",
      {s: round(float(v), 3) for s, v in zip(P['syms'], P['p_leg'])})

def probe_cell(name, cell):
    ent, ext = R.cell_events(P, cell)
    rec = R.run_portfolio(P, ent, ext, cost_fn=side_cost_x2, collect=True)
    st = R.cell_stats(rec["returns"], P["idx"])
    dump_ok = True
    try:
        json.dumps(R._jsonable(
            {"stats": st, "n_trades": rec["n_trades"],
             "n_entries": rec["n_entries"],
             "transitions_head": rec["transitions_head"]}))
    except Exception as exc:
        dump_ok = repr(exc)[:120]
    ev_days = [str(P['idx'][t].date()) for t in np.flatnonzero(ent.any(axis=1))]
    print(f"{name}: entries={rec['n_entries']} trades={rec['n_trades']} "
          f"t1_ok={rec['t1_ok']} sharpe={st['sharpe_full']} "
          f"ann={st['ann_ret']} maxdd={st['max_dd']} "
          f"oos_sharpe={st['oos_sharpe']} rolls={rec['rolls']} "
          f"dump_ok={dump_ok}")
    print(f"  enter_days={ev_days[:12]}")
    return rec, st

probe_cell("SOE_HOLD", R.CELLS[0])
probe_cell("SOE_REPAIR", R.CELLS[3])
probe_cell("SOE_LOWVOL3", R.CELLS[4])
print(f"probe elapsed: {time.time() - t0:.1f}s")
print("PROBE OK")
