# r828 bm-b: inspect queue_head_collision_probe.json conflict sides (ts/verdict)
import sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(r"results\queue_head_collision_probe.json", "rb").read().decode("utf-8")
lines = t.split("\n")
side = None
for i, l in enumerate(lines):
    if l.startswith("<<<<<<<"):
        side = "HEAD"
        print("MARK", i, l[:60])
        continue
    if l.startswith("======="):
        side = "MINE"
        print("MARK", i, l[:60])
        continue
    if l.startswith(">>>>>>>"):
        side = None
        print("MARK", i, l[:60])
        continue
    if side:
        for k in ('"ts"', '"verdict"', '"machine', '"round', '"origin_head"', '"local_head"'):
            if k in l:
                print(side, i, l.strip()[:110])
                break
