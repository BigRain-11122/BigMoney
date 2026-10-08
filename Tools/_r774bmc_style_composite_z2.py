# -*- coding: utf-8 -*-
"""r774 bm-c: library double-shadow composite iteration-3 (z2, luminance-mask).
z verdict: ALL THREE v1/v2 failure causes fixed (two readable separated
figures / zero anachronism / zero hieroglyph drift) but the scaled overlay
reads as a rectangular panel with hard edges + horizontal streaks (craft
flaw, honesty 真实感=5). Mechanical fix: per-pixel luminance mask on the
overlay (soft ramp above T=90, steepened ^1.5) kills the panel background
and streaks while keeping the rim-lit figure -- true double-exposure ghost,
no rectangle. Same base3 + same side=right placement + same 45% scale.
Output: results/mv_work/kf/st1_library_z2_composite.png + stats receipt."""
import json
import os
import time

import numpy as np
from PIL import Image

KF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
T = 90.0
POWER = 1.5
STRENGTH = 0.85
SCALE = 0.45


def main():
    base = Image.open(os.path.join(KF, "st1_library_base3.png")).convert("RGB")
    over = Image.open(os.path.join(KF, "st1_scribe_overlay3.png")).convert("RGB")
    W, H = base.size
    ow, oh = int(W * SCALE), int(H * SCALE)
    over_small = over.resize((ow, oh), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(over_small, (int(W * 0.52), int(H * 0.30)))
    b = np.asarray(base, dtype=np.float32)
    c = np.asarray(canvas, dtype=np.float32)
    L = c.mean(axis=2)
    stats = {"p50": float(np.percentile(L, 50)), "p90": float(np.percentile(L, 90)),
             "p99": float(np.percentile(L, 99)),
             "above_T_pct": float((L > T).mean() * 100)}
    mask = np.clip((L - T) / (255.0 - T), 0.0, 1.0) ** POWER * STRENGTH
    m3 = mask[:, :, None]
    out = b + (255.0 - b) * m3
    comp = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    out_p = os.path.join(KF, "st1_library_z2_composite.png")
    comp.save(out_p)
    receipt = {"round": "r774 bm-c", "composite": "z2",
               "method": "luminance-mask double exposure (panel-edge kill)",
               "T": T, "power": POWER, "strength": STRENGTH, "scale": SCALE,
               "pos": [int(W * 0.52), int(H * 0.30)], "stats": stats,
               "bytes": os.path.getsize(out_p),
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rp = os.path.join(KF, "style_v7_z2_receipt.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("Z2 saved %s %dB stats=%s receipt=%s"
          % (out_p, os.path.getsize(out_p), stats, rp))


if __name__ == "__main__":
    main()
