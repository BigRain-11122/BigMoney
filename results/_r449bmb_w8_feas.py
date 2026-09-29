"""Feasibility probe: replay ONE member sleeve via t27 verbatim machinery
(member_run_iv6 from iv6_portfolio) and reconcile stats vs the frozen
portfolio_blend_tournament.json members face (x1). Read-only, no writes."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iv6_portfolio import member_run_iv6, _init_worker

_init_worker()  # sets ew6_portfolio.PRICES_FULL in-process
t0 = time.time()
r = member_run_iv6("COMPOSITE-CE-01", None)
el = time.time() - t0
print("elapsed_sec:", round(el, 1))
print("cutoff:", r.get("cutoff"))
x1 = r.get("full", {})
print("x1 full face:", json.dumps({k: x1.get(k) for k in ("sharpe", "ann", "maxdd", "n_trades", "n_entries") if k in x1}, ensure_ascii=False))
print("n dates:", len(r.get("dates", [])), "| first:", r.get("dates", ["?"])[0], "| last:", r.get("dates", ["?"])[-1])
print("eq head:", r.get("eq", [])[:3])

frozen = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_blend_tournament.json"), encoding="utf-8"))
m = frozen["members"]["COMPOSITE-CE-01"]["x1"]
print("frozen x1:", json.dumps(m, ensure_ascii=False)[:300])
