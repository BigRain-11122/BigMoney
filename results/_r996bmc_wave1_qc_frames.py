# -*- coding: utf-8 -*-
# r996 wave-1 3-frame QC sheet (O-20261014-1325 item-1: 每条出炉即抽 3 帧自检)
import subprocess, os, sys
from PIL import Image

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
SHOTS = ["SING1_torch_song_v2_s9013", "SING2_firepit_song_s9014", "SING3b_morning_song_open_v4_s9019"]
OUT = os.path.join(BMC, "wave1_qc_frames")
os.makedirs(OUT, exist_ok=True)

cells = []
for tag in SHOTS:
    mp4 = os.path.join(BMC, "i2v", tag + ".mp4")
    for k, pos in enumerate(("1", "2.5", "4"), 1):  # ~1s/2.5s/4s of a ~5s clip
        jpg = os.path.join(OUT, "%s_f%d.jpg" % (tag, k))
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", pos, "-i", mp4,
                            "-frames:v", "1", "-q:v", "4", jpg], capture_output=True)
        if r.returncode == 0 and os.path.exists(jpg):
            cells.append((tag, k, jpg))
        else:
            print("EXTRACT FAIL", tag, k, r.stderr.decode()[:200])

# 3x3 contact sheet
thumb_w = 480
rows = []
imgs = []
for tag, k, jpg in cells:
    im = Image.open(jpg)
    h = int(im.height * thumb_w / im.width)
    imgs.append((tag, k, im.resize((thumb_w, h))))
if imgs:
    th = imgs[0][2].height
    sheet = Image.new("RGB", (thumb_w * 3 + 16, th * 3 + 16), (12, 12, 12))
    for i, (tag, k, im) in enumerate(imgs):
        x = (i % 3) * (thumb_w + 4) + 4
        y = (i // 3) * (th + 4) + 4
        sheet.paste(im, (x, y))
    dst = os.path.join(BMC, "wave1_qc_sheet_r996.jpg")
    sheet.save(dst, quality=88)
    print("SHEET:", dst, sheet.size, "cells:", len(imgs))
else:
    print("NO FRAMES EXTRACTED")
