# -*- coding: utf-8 -*-
"""r683 bm-a W117 seat receipt: capture pre-seat probe output + live chain heads (ledger head derive, zero hand-copy)."""
import subprocess
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import science_gates

r = subprocess.run([sys.executable, os.path.join(ROOT, "results", "_r683bma_w117_probe.py")],
                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
lines = [f"[probe rc={r.returncode}]"]
lines += r.stdout.splitlines()
if r.returncode != 0:
    lines += ["STDERR:", r.stderr]
lines += ["[heads] global trials ledger head = " + str(science_gates.ledger_head())
          if hasattr(science_gates, "ledger_head") else "[heads] ledger_head() n/a"]
open(os.path.join(ROOT, "results", "_r683bma_w117_probe_receipt.txt"), "w",
     encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("receipt written; probe rc =", r.returncode)
print(lines[-1])
