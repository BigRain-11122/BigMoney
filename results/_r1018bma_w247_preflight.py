# -*- coding: utf-8 -*-
# r1018 bm-a: W247 seat pre-flight facts (origin faces + registry state)
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, creationflags=0x08000000)

out = subprocess.check_output(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                                "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                               encoding="utf-8", errors="replace")
lines = out.splitlines()
w246_seat = [ln for ln in lines if "w246" in ln.lower() and "seat" in ln.lower()]
w247_seat = [ln for ln in lines if "w247" in ln.lower() and "seat" in ln.lower()]
print("w246_seat_on_origin:", w246_seat)
print("w247_seat_on_origin:", w247_seat)

out_pf = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces.py"], cwd=ROOT,
                                  encoding="utf-8", errors="replace")
print("W247 row on origin pf:", '247: {"a": (' in out_pf)
print("W246 row on origin pf:", '246: {"a": (' in out_pf)
out_n1 = subprocess.check_output(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"], cwd=ROOT,
                                  encoding="utf-8", errors="replace")
print("W247 WAVE_CONFIGS on origin n1:", '"PERPETUAL-N1-W247"' in out_n1)
pre = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                               "research/PERPETUAL_N1_W247_PREREG.md"], cwd=ROOT,
                              encoding="utf-8", errors="replace").strip()
print("W247 prereg on origin:", bool(pre))

# registry live state
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from perpetual_faces import N1_BANDS
print("rows:", len(N1_BANDS), "tail key:", max(N1_BANDS))
w246 = N1_BANDS.get(246)
print("W246 bands:", {"a": w246["a"], "b_exit": w246["b_exit"], "engine_owner": w246.get("engine_owner")})
w239 = N1_BANDS.get(239)
print("W239 bands:", {"a": w239["a"], "b_exit": w239["b_exit"], "engine_owner": w239.get("engine_owner")})
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
bmc = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
print("owner_rows:", len(owner_rows), "bma:", len(bma), "bmb:", len(bmb), "bmc:", len(bmc))
print("w246 results exists:", os.path.exists(os.path.join(ROOT, "results", "perpetual_faces", "n1_w246_results.json")))

# recent origin commits by other machines (W247 collision face)
lg = subprocess.check_output(["git", "log", "origin/main", "-12", "--format=%h %s"], cwd=ROOT,
                             encoding="utf-8", errors="replace")
print("--- origin log tail ---")
print(lg)
