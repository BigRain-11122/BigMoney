# -*- coding: utf-8 -*-
"""r770 bm-c: library double-shadow composite iteration-2.
base = st1_library_base2 (lamp-safe), overlay = st1_scribe_overlay2 (wide
full-body figure). Screen blend, alpha 0.75. Output:
results/mv_work/kf/st1_library_y_composite.png"""
from PIL import Image, ImageChops

KF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
base = Image.open(KF + r"\st1_library_base2.png").convert("RGB")
over = Image.open(KF + r"\st1_scribe_overlay2.png").convert("RGB")
if base.size != over.size:
    over = over.resize(base.size, Image.LANCZOS)
screen = ImageChops.screen(base, over)
comp = Image.blend(base, screen, 0.75)
out = KF + r"\st1_library_y_composite.png"
comp.save(out)
print("saved %s %dB size=%s" % (out, len(open(out, "rb").read()), comp.size))
