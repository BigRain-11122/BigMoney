import ast
import inspect

for f in ["run_tick.py", "run_daily.py", "report.py", "evolve.py", "backtest.py",
          "strategies.py", "regime.py", "data.py", "config.py"]:
    ast.parse(open(rf"E:\Money\{f}", encoding="utf-8").read())
print("ALL SYNTAX OK")

import evolve
import report

print("write_signals params:", list(inspect.signature(report.write_signals).parameters))
src = inspect.getsource(evolve.deepen)
for key in ["live", "cache", "regime", "out_dir"]:
    assert f'"{key}"' in src, f"deepen missing key {key}"
print("tick wiring consistent")
