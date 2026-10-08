# -*- coding: utf-8 -*-
"""r770 bm-c: library double-shadow composite (post-production beat).
base = st1_library_c (v2 clean filmic archive, photographic fixes landed),
overlay = st1_scribe_overlay (single-figure frame, SDXL-proven easy).
Screen blend keeps dark base intact (night archive) and lets the lit scribe
figure ghost through = double-exposure BY CONSTRUCTION. Alpha 0.8 keeps base
weight. Output: results/mv_work/kf/st1_library_x_composite.png."""
from PIL import Image, ImageChops

KF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
base = Image.open(KF + r"\st1_library_c.png").convert("RGB")
over = Image.open(KF + r"\st1_scribe_overlay.png").convert("RGB")
if base.size != over.size:
    over = over.resize(base.size, Image.LANCZOS)
screen = ImageChops.screen(base, over)
comp = Image.blend(base, screen, 0.8)
out = KF + r"\st1_library_x_composite.png"
comp.save(out)
print("saved %s %dB size=%s" % (out, len(open(out, "rb").read()), comp.size))
