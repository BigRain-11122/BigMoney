# -*- coding: utf-8 -*-
# r581 bm-b: r511 tail-lock pre-seat check (W97 vacancy + anchor state)
import subprocess
subprocess.run(["git", "fetch", "origin"], capture_output=True)


def show(path):
    r = subprocess.run(["git", "show", "origin/main:" + path],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace")


out = show("scripts/perpetual_faces.py")
print("W97 pf row on origin:", '97: {"a"' in out)
outn = show("scripts/perpetual_faces_n1.py")
print("W97 WAVE_CONFIGS on origin:", '"PERPETUAL-N1-W97"' in outn)
ls = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                     "--", "fleet/inbox/", "fleet/inbox/processed/"],
                    capture_output=True).stdout.decode("utf-8", "replace")
w97 = [l for l in ls.splitlines() if "w97" in l.lower()]
print("W97 seat MSGs on origin:", w97 or "NONE")
pr = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                     "research/PERPETUAL_N1_W97_PREREG.md"],
                    capture_output=True).stdout.decode("utf-8", "replace").strip()
print("W97 prereg on origin:", pr or "NONE")
r2 = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                    "results/perpetual_faces/n1_w92_results.json"],
                    capture_output=True).stdout.decode("utf-8", "replace").strip()
print("W92 finalize on origin:", r2 or "NOT-YET")
ll = subprocess.run(["git", "ls-tree", "--name-only", "origin/main",
                     "results/perpetual_faces/"],
                    capture_output=True).stdout.decode("utf-8", "replace")
n1res = sorted([l.split("/")[-1] for l in ll.splitlines() if "n1_w" in l],
               key=lambda x: int(x.split("w")[1].split("_")[0]))
print("latest landed n1 finalize:", n1res[-1])
