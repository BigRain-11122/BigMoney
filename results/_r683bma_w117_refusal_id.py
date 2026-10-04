# -*- coding: utf-8 -*-
"""r683 bm-a: identify the refusing registered band (63_050, 65_049) for the W117 prereg wording."""
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
for w, cfg in sorted(N1_BANDS.items()):
    for key in ("a", "b_exit"):
        lo, hi = cfg[key]
        if (lo, hi) == (63_050, 65_049):
            print(f"band ({lo}, {hi}) = W{w}.{key} engine_owner={cfg.get('engine_owner')}")
