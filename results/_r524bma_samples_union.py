# r524 bm-a: pool_core_samples.jsonl minimal surgical union.
# origin face (LF) + append the one local-unique n1w12-11of12 sample line.
import subprocess

path = "results/pool_core_samples.jsonl"
origin = subprocess.check_output(["git", "show", "origin/main:" + path])
cur = open(path, "rb").read()
mine = [l for l in cur.splitlines() if b"n1w12-11of12" in l]
assert len(mine) == 1, f"expected 1 unique line, got {len(mine)}"
content = origin.rstrip(b"\n") + b"\n" + mine[0] + b"\n"
open(path, "wb").write(content)
print("total lines:", content.count(b"\n"))
