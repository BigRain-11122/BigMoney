t = open("scripts/perpetual_faces_n1.py", encoding="utf-8").read()
# selftest-region T-141 leg (indented comment, inside selftest)
k = t.find("def selftest() -> int:")
i = t.find("    # --- T-141 s2 lane face", k)
print("--- selftest T-141 leg anchor context (before 240) ---")
print(repr(t[i - 240:i + 80]))
# what leg ends right before it? find last 'materializer face' block start
import re
legs = [m.start() for m in re.finditer(r"    # --- W\d+ materializer face", t[k:])]
print("materializer legs found:", len(legs))
last_leg = None
for m in re.finditer(r"    # --- (W\d+) materializer face", t[k:]):
    last_leg = m.group(1)
print("last leg before selftest-T141:", last_leg)
