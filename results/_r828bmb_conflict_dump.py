# r828 bm-b: full dump of probe JSON conflict sides
import sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(r"results\queue_head_collision_probe.json", "rb").read().decode("utf-8")
print(t)
