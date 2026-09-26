# r247 contract probe: read science_gates internals for cn_rev_tilt_p1 runner wiring
import re, io

src = io.open("scripts/science_gates.py", encoding="utf-8").read()

m = re.search(r'"cn_rev_tilt_p1".*', src)
print("SEED_ENTRY:", m.group(0)[:100] if m else "MISSING")

m = re.search(r"def n_eff.*?(?=\ndef )", src, re.S)
print("N_EFf:\n", m.group(0)[:800] if m else "MISSING")

m = re.search(r'def null_sharpes.*?(?=\ndef )', src, re.S)
print("NULL_SHARPES:\n", m.group(0)[:600] if m else "MISSING")

m = re.search(r'if pool == "stock_b_layer".*?(?=\n    if pool ==|\n\ndef )', src, re.S)
print("STOCK_B_LAYER_POOL:\n", m.group(0)[:700] if m else "MISSING")

m = re.search(r"def bootstrap_ci_sharpe.*?(?=\ndef )", src, re.S)
print("BOOT:\n", (m.group(0)[:500] if m else "MISSING"))
