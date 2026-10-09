# -*- coding: utf-8 -*-
"""r908 bm-a W195 prereg build-window fact probe (seat/FF/vacancy/registry)."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"


def git(*a):
    r = subprocess.run([GIT, "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()


subprocess.run([GIT, "-C", G, "fetch", "origin"], capture_output=True)

seat = git("log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
           "--", "fleet/inbox/MSG-2026-10-09-0844-bma-w195-seat.md")
print("seat add commit:", seat)
print("inbox file exists:", os.path.exists(
    os.path.join(G, "fleet/inbox/MSG-2026-10-09-0844-bma-w195-seat.md")))

w194_ff = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '194: {"a": (441_604', "--", "scripts/perpetual_faces.py")
print("W194 FF:", w194_ff)
w193_ff = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
              '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
print("W193 FF:", w193_ff)
w195_vac = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
               '195: {"a": (443_804', "--", "scripts/perpetual_faces.py")
print("W195 vacancy (expect empty):", repr(w195_vac))

f193 = git("ls-tree", "origin/main", "results/perpetual_faces/n1_w193_results.json")
f194 = git("ls-tree", "origin/main", "results/perpetual_faces/n1_w194_results.json")
print("n1_w193_results on origin:", "LANDED" if f193 else "MISSING")
print("n1_w194_results on origin:", "LANDED" if f194 else "MISSING")

sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as sg  # noqa: E402
print("SEED_REGISTRY live count:", len(sg.SEED_REGISTRY))
ws = [int(x) for x in sg.SEED_REGISTRY.values() if isinstance(x, int)]
ov = [s for s in ws if 443804 <= s <= 446003]
print("W195 band overlap (expect []):", ov[:5])
print("registry-count face in src:",
      open(os.path.join(G, "results/_r908bma_w195_prereg_src.txt"),
           encoding="utf-8").read().count("SEED_REGISTRY \u5168\u952e 194 \u503c"))
