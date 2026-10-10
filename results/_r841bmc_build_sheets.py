# -*- coding: utf-8 -*-
# r841 KF QC contact sheets: 6 frames per sheet (3x2), labeled cells.
import os, sys
from PIL import Image, ImageDraw

D = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\frames_full"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r841bmc_qc_sheets"
os.makedirs(OUT, exist_ok=True)

skip = {"B01_weary", "B02_far_home"}  # regenerating with fixed prompt
ids = sorted(f[:-4] for f in os.listdir(D) if f.endswith(".png") and f[:-4] not in skip)
CELL_W, CELL_H, LABEL_H = 800, 457, 34  # 1344x768 scaled by ~0.596

COLS, ROWS = 2, 3
PER = COLS * ROWS
sheets = []
for s in range(0, len(ids), PER):
    chunk = ids[s:s+PER]
    W = COLS * CELL_W
    H = ROWS * (CELL_H + LABEL_H)
    img = Image.new("RGB", (W, H), (24, 24, 24))
    dr = ImageDraw.Draw(img)
    for i, sid in enumerate(chunk):
        r, c = divmod(i, COLS)
        x0, y0 = c * CELL_W, r * (CELL_H + LABEL_H)
        dr.rectangle([x0, y0, x0 + CELL_W - 1, y0 + LABEL_H - 1], fill=(0, 0, 0))
        dr.text((x0 + 10, y0 + 8), "%02d  %s" % (s + i + 1, sid), fill=(255, 230, 150))
        im = Image.open(os.path.join(D, sid + ".png")).convert("RGB").resize((CELL_W, CELL_H), Image.LANCZOS)
        img.paste(im, (x0, y0 + LABEL_H))
    path = os.path.join(OUT, "QC_SHEET_%02d.png" % (s // PER + 1))
    img.save(path, optimize=True)
    sheets.append((path, chunk))
    print(path, "frames=%d" % len(chunk), " ".join(chunk))
print("TOTAL sheets=%d frames=%d" % (len(sheets), len(ids)))
