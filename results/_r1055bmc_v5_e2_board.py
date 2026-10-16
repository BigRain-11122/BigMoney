# -*- coding: utf-8 -*-
"""r1055 bm-c harvest QC step 2: rebuild CHK-E2 board with the correct female-anchor
shots (E03/E04/R06/SIL4 per V5 spec sec.3/sec.6) + individual large frames."""
import os, subprocess, io
from PIL import Image, ImageDraw

BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\i2v\v5redo"
OUTDIR = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
TH = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\v5redo\_thumbs_p2_r1054\femanchor2_r1055"
os.makedirs(TH, exist_ok=True)

# female-anchor shots per spec sec.3 (ID_F_2001): thick blunt bangs + long straight
# black hair + cream knit top; hair-bun (发髻) = fail
FEM = [
    ("E03", "E03_gaze_meet_v5.mp4"),
    ("E04", "E04_replay_faces_v5.mp4"),
    ("R06", "R06_museum_verse_v5.mp4"),
    ("SIL4", "SIL4_crowd_edge_v5.mp4"),
]
times = ["0.8", "1.7", "2.6", "3.5", "4.3"]
W, Hc = 640, 360
cols = len(times)
rows = len(FEM)
board = Image.new("RGB", (W * cols, Hc * rows + 26), (18, 18, 18))
dr = ImageDraw.Draw(board)
dr.text((8, 4), "JAY-V5 CHK-E2 FEMALE-ANCHOR BOARD (ID_F_2001: thick blunt bangs + long straight black hair + cream knit; hair-BUN = FAIL) r1055", fill=(255, 220, 120))
for r, (tag, fn) in enumerate(FEM):
    p = os.path.join(BASE, fn)
    for c, tm in enumerate(times):
        fp = os.path.join(TH, "%s_t%d.jpg" % (tag, c))
        subprocess.run(["ffmpeg", "-y", "-ss", tm, "-i", p, "-frames:v", "1",
                         "-q:v", "2", fp], capture_output=True)
        if os.path.exists(fp):
            im = Image.open(fp)
            im.thumbnail((W - 6, Hc - 22))
            board.paste(im, (c * W + 3, r * Hc + 24))
            dr.text((c * W + 8, r * Hc + 6), "%s t=%ss" % (tag, tm), fill=(200, 255, 160))
out = os.path.join(OUTDIR, "JAY-V5-CHK-E2-FEMALE-ANCHOR-BOARD-r1055.jpg")
board.save(out, quality=88)
print("CHK-E2 board ->", out)

# individual large frames for E03/E04 (spec sec.6: 单独大图比对板)
for tag, fn in [("E03", "E03_gaze_meet_v5.mp4"), ("E04", "E04_replay_faces_v5.mp4")]:
    src = os.path.join(TH, "%s_t2.jpg" % tag)  # mid timepoint 2.6s
    dst = os.path.join(OUTDIR, "JAY-V5-CHK-E2-%s-LARGE-r1055.jpg" % tag)
    im = Image.open(src)
    im.save(dst, quality=92)
    print("large frame ->", dst, im.size)
print("STEP2 DONE")
