import os
import sys

import numpy as np

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import t23_random_grammar_census as t23  # noqa: E402

rng = np.random.default_rng(1)
leaves = {"VOLUME": rng.uniform(1e6, 2e6, size=(2, 200))}
node = t23.formula_str and None
# build tree for DELTA(VOLUME,30) via direct tuple
tree = ("roll", "DELTA", 30, ("leaf", "VOLUME"))
arr = t23.evaluate(tree, leaves)
print("DELTA shape:", np.asarray(arr).shape)
print("n finite:", int(np.isfinite(arr).sum()), "of", arr.size)

tree2 = ("un", "CSRANK", ("leaf", "VOLUME"))
arr2 = t23.evaluate(tree2, leaves)
print("CSRANK on 2x200 unique per date:", np.unique(arr2[:, -1]))

# single row
leaves1 = {"VOLUME": rng.uniform(1e6, 2e6, size=(1, 200))}
arr1 = t23.evaluate(tree, leaves1)
print("single-row DELTA n finite:", int(np.isfinite(arr1).sum()))
