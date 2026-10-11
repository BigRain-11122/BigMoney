"""r902: W211 ignition check + perpetual_faces CLI probe."""
import re

src = open(r"scripts\perpetual_faces.py", encoding="utf-8").read()
m = re.search(r"N1_BANDS\s*=\s*\{(.*?)\n\}", src, re.S)
keys = re.findall(r"^\s{4}(\d+):", m.group(1), re.M)
print("N1_BANDS registered waves:", len(keys), "| has 211:", "211" in keys, "| has 210:", "210" in keys)
m2 = re.search(r"\n    211: \{(.*?)\}", m.group(1), re.S)
print("W211 entry:", (m2.group(1)[:400] if m2 else "NOT FOUND"))

args = re.findall(r"add_argument\(['\"]([^'\"]+)['\"]", src)
print("CLI args:", args[:16])
