# r828 bm-b: diagnose history jsonl conflict sides (line-level)
import sys
sys.stdout.reconfigure(encoding="utf-8")

p = r"results\saturation_engine\history_bm-b.jsonl"
t = open(p, "rb").read().decode("utf-8")
a, b, cur = [], [], None
for line in t.split("\n"):
    if line.startswith("<<<<<<<"):
        cur = a
    elif line.startswith("======="):
        cur = b
    elif line.startswith(">>>>>>>"):
        cur = None
    elif cur is not None:
        cur.append(line)
h_lines = [x for x in a if x.strip()]
r_lines = [x for x in b if x.strip()]
print("HEAD side lines:", len(h_lines), " replay side lines:", len(r_lines))
print("HEAD last 2:")
for x in h_lines[-2:]:
    print("  ", x.strip()[:130])
print("REPLAY last 2:")
for x in r_lines[-2:]:
    print("  ", x.strip()[:130])
# CR-normalized comparison
hn = {x.replace("\r", "") for x in h_lines}
rn = {x.replace("\r", "") for x in r_lines}
print("replay subset of HEAD after CR-normalize:", rn <= hn)
print("replay-only lines (normalized):", len(rn - hn))
for x in list(rn - hn)[:3]:
    print("  only-in-replay:", x[:130])
print("HEAD-only lines (normalized):", len(hn - rn))
for x in list(hn - rn)[:3]:
    print("  only-in-head:", x[:130])
