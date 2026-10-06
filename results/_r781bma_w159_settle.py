# -*- coding: utf-8 -*-
"""r781 pre-freeze settle legs: (1) r779 probe dumps vs r781 probe dumps
byte-equality (zero drift of the W158 faces since the r779 session);
(2) seat MSG processed-move commit history (who/when for the honest
self-ack prose); (3) probe receipt verdict + band parity."""
import filecmp
import json
import subprocess

pairs = [
    (r"results\_r779bma_w159_pf_block158.txt", r"results\_r781bma_w159_probe_pf_block.txt"),
    (r"results\_r779bma_w159_entry158.txt", r"results\_r781bma_w159_probe_n1_entry.txt"),
    (r"results\_r779bma_w159_mat_block.txt", r"results\_r781bma_w159_probe_n1_mat.txt"),
    (r"results\_r779bma_w159_claim158.txt", r"results\_r781bma_w159_probe_n1_claim.txt"),
]
for a, b in pairs:
    print("DRIFT-CHECK", a.split("\\")[-1], "==", filecmp.cmp(a, b, shallow=False))

p = subprocess.run(["git", "log", "--oneline", "--follow", "--format=%h %s",
                    "-3", "--", "fleet/inbox/processed/MSG-2026-10-06-142x-bma-w159-seat.md"],
                   capture_output=True).stdout.decode("utf-8", errors="replace")
print("SEAT MSG processed history:")
print(p)

d = json.load(open(r"results\_r779bma_w159_probe_receipt.json", encoding="utf-8"))
print("probe receipt verdict:", d.get("verdict"), "| bands:", d.get("bands"))
g = json.load(open(r"results\_r779bma_w159_band_gate.json", encoding="utf-8"))
print("gate verdict:", g["verdict"], "| leg1 parity:", g["legs"]["leg1"].get("parity_with_probe"))
