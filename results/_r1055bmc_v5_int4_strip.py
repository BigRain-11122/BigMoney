# -*- coding: utf-8 -*-
"""r1055 bm-c harvest QC step 3: INT4 6-frame recheck strip."""
import os
from PIL import Image, ImageDraw

D = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\v5redo\_thumbs_p2_r1054\int4_recheck_r1055"
OUT = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\JAY-V5-INT4-RECHECK-STRIP-r1055.jpg"
fs = sorted(f for f in os.listdir(D) if f.endswith(".jpg"))
W, Hc = 640, 360
board = Image.new("RGB", (W * len(fs), Hc + 24), (18, 18, 18))
dr = ImageDraw.Draw(board)
dr.text((8, 4), "INT4_rubbing_v5 recheck strip (seed 9907; V4 defect = in-source phantom dissolve/double-exposure; fix = single continuous pose) r1055", fill=(255, 220, 120))
for i, f in enumerate(fs):
    im = Image.open(os.path.join(D, f))
    im.thumbnail((W - 6, Hc - 6))
    board.paste(im, (i * W + 3, 22))
board.save(OUT, quality=88)
print("strip ->", OUT)
