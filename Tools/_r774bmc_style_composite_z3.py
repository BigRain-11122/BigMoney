# -*- coding: utf-8 -*-
"""r774 bm-c: library composite iteration-4 (z3, dark-silhouette multiply
ghost). Grid evidence: overlay3 = light panel (~205, 71% px) + dark core
figure (~4-21, 8% px) -- the 'pure black background' prompt FAILED, so any
screen/luminance-add blend re-projects the panel rectangle (z/z2 verdict).
Mechanical fix: dark-side mask (TH=150, soft blur) -> multiply ghost: figure
darkens the base as a translucent backlit silhouette, panel contributes zero
(mask=0 outside figure). Same base3 + right-side 45% placement as z/z2.
Output: results/mv_work/kf/st1_library_z3_composite.png + receipt."""
import json
import os
import time

import numpy as np
from PIL import Image, ImageFilter

KF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
TH = 150.0
LMIN = 8.0
STRENGTH = 0.55
BLUR = 2.0
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
    L = np.asarray(canvas.convert("L"), dtype=np.float32)
    mask = np.clip((TH - L) / (TH - LMIN), 0.0, 1.0) ** 0.9
    # paste-region indicator: the black canvas margin is also < TH and must
    # NOT become ghost (dark_mask x region, else 55% global darkening)
    region = np.zeros((H, W), dtype=np.float32)
    x0, y0 = int(W * 0.52), int(H * 0.30)
    region[y0:y0 + oh, x0:x0 + ow] = 1.0
    mask = mask * region
    mimg = Image.fromarray((mask * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(BLUR))
    m = np.asarray(mimg, dtype=np.float32) / 255.0
    out = b * (1.0 - m[:, :, None] * STRENGTH)
    comp = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    out_p = os.path.join(KF, "st1_library_z3_composite.png")
    comp.save(out_p)
    receipt = {"round": "r774 bm-c", "composite": "z3",
               "method": "dark-silhouette multiply ghost (panel-proof)",
               "TH": TH, "lmin": LMIN, "strength": STRENGTH, "blur": BLUR,
               "scale": SCALE, "pos": [int(W * 0.52), int(H * 0.30)],
               "mask_nonzero_pct": float((m > 0.02).mean() * 100),
               "bytes": os.path.getsize(out_p),
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    rp = os.path.join(KF, "style_v7_z3_receipt.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("Z3 saved %s %dB mask_nonzero=%.1f%% receipt=%s"
          % (out_p, os.path.getsize(out_p), receipt["mask_nonzero_pct"], rp))


if __name__ == "__main__":
    main()
