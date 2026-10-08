# -*- coding: utf-8 -*-
"""r770 bm-c: O-1820 review-package jpg converter (order law: 样图转 jpg).
Inputs (5): st3_goddess_b, st4_glass_a, st1_library_x_composite,
st1_library_y_composite, st2_carve_f. Output:
results/mv_work/outbound_jpg/<name>.jpg (quality 88, full 1024x576)."""
from PIL import Image
import os

KF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\outbound_jpg"
NAMES = ["st3_goddess_b", "st4_glass_a", "st1_library_x_composite",
         "st1_library_y_composite", "st2_carve_f"]

os.makedirs(OUT, exist_ok=True)
for n in NAMES:
    img = Image.open(os.path.join(KF, n + ".png")).convert("RGB")
    dst = os.path.join(OUT, n + ".jpg")
    img.save(dst, "JPEG", quality=88)
    print("%s -> %dB" % (n, os.path.getsize(dst)))
