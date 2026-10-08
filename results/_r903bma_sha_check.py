# -*- coding: utf-8 -*-
import subprocess
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
def g(*a):
    return subprocess.run(["git", "-C", G] + list(a),
                          capture_output=True).stdout.decode("utf-8", "replace").strip()
print("w193ff_pick=", repr(g("log", "origin/main", "--format=%h", "-n", "1", "-S",
      '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")))
print("w192ff_pick=", repr(g("log", "origin/main", "--format=%h", "-n", "1", "-S",
      '192: {"a": (437_204', "--", "scripts/perpetual_faces.py")))
print("w191ff_pick=", repr(g("log", "origin/main", "--format=%h", "-n", "1", "-S",
      '191: {"a": (435_004', "--", "scripts/perpetual_faces.py")))
print("w194vacancy=", repr(g("log", "origin/main", "--format=%h", "-n", "1", "-S",
      '194: {"a": (441_604', "--", "scripts/perpetual_faces.py")))
print("seat_add=", repr(g("log", "origin/main", "--format=%h", "-n", "1",
      "--diff-filter=A", "--", "fleet/inbox/MSG-2026-10-09-0627-bma-w194-seat.md")))
print("w192fin=", repr(g("ls-tree", "origin/main",
      "results/perpetual_faces/n1_w192_results.json")))
print("w193fin=", repr(g("ls-tree", "origin/main",
      "results/perpetual_faces/n1_w193_results.json")))
