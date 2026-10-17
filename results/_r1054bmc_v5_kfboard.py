# -*- coding: utf-8 -*-
# Build contact sheet of the 10 non-trial V5 KFs (frame-gate before phase2 ignition)
from PIL import Image, ImageDraw
import os
KFDIR = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\v5redo\kf_r1054"
OUT = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\V5-NONTRIAL-KF-BOARD-r1054.jpg"
ids = ["C01_carver_face_v5_s9913","D01_carver_words_v5_s9914","D03b_direct_gaze_v5_s9915","E01c_first_line_v5_s9916",
       "E03_gaze_meet_v5_s9917","R06_museum_verse_v5_s9918","E04_replay_faces_v5_s9919","C04_words_alive_v5_s9920",
       "D05_words_warm_v5_s9921","SIL1_babylon_v5_s9922"]
tw, thh, lab, cols = 448, 253, 22, 5
rows_n = (len(ids) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 6) + 6, rows_n * (thh + lab + 6) + 34), (24, 20, 16))
dr = ImageDraw.Draw(sheet)
dr.text((10, 6), "V5 non-trial KFs (10) -- frame gate -- bm-c r1054", fill=(240, 200, 120))
for ci, tag in enumerate(ids):
    p = os.path.join(KFDIR, tag + ".png")
    pic = Image.open(p).convert("RGB").resize((tw, thh))
    x = 6 + (ci % cols) * (tw + 6); y = 34 + (ci // cols) * (thh + lab + 6)
    dr.text((x + 4, y + 3), tag, fill=(225, 205, 150))
    sheet.paste(pic, (x, y + lab))
    dr.rectangle([x, y + lab, x + tw, y + lab + thh], outline=(90, 40, 40))
sheet.save(OUT, "JPEG", quality=88)
print("BOARD-OK", OUT, os.path.getsize(OUT))
