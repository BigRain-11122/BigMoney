# _r889bmc_slice5_probe.py -- zero-burn data probe: lowamp axis panel calendars
# (slice5 date-axis recoverability check; read-only data loading)
import importlib.util
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

spec = importlib.util.spec_from_file_location(
    "lp3", os.path.join(ROOT, "scripts", "lowamp_p3.py"))
lp3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lp3)

out = []
try:
    from live.paper import build_panels
    for axis in ("legacy", "deep"):
        prices = lp3.load_axis(axis)
        close = build_panels(prices)["close"]
        idx = close.index
        out.append(f"{axis} panel_len={len(idx)} first={idx[0].date()} "
                   f"last={idx[-1].date()} members={len(prices)}")
except Exception:
    out.append("PROBE-FAIL:\n" + traceback.format_exc())

with open(os.path.join(ROOT, "results", "_r889bmc_slice5_probe.txt"),
          "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))
