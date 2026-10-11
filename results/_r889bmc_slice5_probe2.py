# _r889bmc_slice5_probe2.py -- zero-burn probe: panel dates vs REGIME-5 label
# calendar coverage (set containment + unlabeled residue census)
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

spec = importlib.util.spec_from_file_location(
    "lp3", os.path.join(ROOT, "scripts", "lowamp_p3.py"))
lp3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lp3)

from live.paper import build_panels  # noqa: E402

reg5 = json.load(open(os.path.join(
    ROOT, "results", "regime5_labels", "REGIME5-2026-09-30.json"),
    encoding="utf-8"))
label_days = {l["date"] for l in reg5["labels"]}
panic = json.load(open(os.path.join(
    ROOT, "results", "regime_axis_m1", "panic_windows.json"),
    encoding="utf-8"))
panic_days = {x["date"] for x in panic["days"]}

out = []
for axis in ("legacy", "deep"):
    prices = lp3.load_axis(axis)
    idx = build_panels(prices)["close"].index
    ds = [str(d.date()) for d in idx]
    in_labels = sum(1 for d in ds if d in label_days)
    in_panic = sum(1 for d in ds if d in panic_days)
    pre_floor = sum(1 for d in ds if d < "2013-03-21")
    residue = [d for d in ds
               if d not in label_days and d not in panic_days
               and d >= "2013-03-21"]
    out.append(f"{axis}: n={len(ds)} in_labels={in_labels} in_panic={in_panic} "
               f"pre_floor={pre_floor} residue={len(residue)} "
               f"first={ds[0]} last={ds[-1]}")
    if residue:
        out.append("  residue sample: " + ",".join(residue[:10]))

with open(os.path.join(ROOT, "results", "_r889bmc_slice5_probe2.txt"),
          "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))
