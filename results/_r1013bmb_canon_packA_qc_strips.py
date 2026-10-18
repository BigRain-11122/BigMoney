# -*- coding: utf-8 -*-
# packA_qc_strips.py -- 星晴PACK-A烧后帧检条板生成 (SIGN §四 18项注册表的判读底板·bank job)
import os, subprocess, sys
from PIL import Image, ImageDraw

REPO = r"K:\Fluxgroup\FluxGroup"
CLIPS = os.path.join(REPO, "media", "mv-album-001-jay", "clips-packA-768")
TMP = os.path.join(CLIPS, "_qcframes")
OUT = os.path.join(REPO, "cph4", "fleet", "mv-album-001-jay", "xq-PACKA-QC-STRIPS-20261018.jpg")
NO_WINDOW = 0x08000000
os.makedirs(TMP, exist_ok=True)

def ff(clip, t, outpng):
    r = subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", clip, "-frames:v", "1", outpng],
                       capture_output=True, creationflags=NO_WINDOW, timeout=120)
    return r.returncode == 0 and os.path.isfile(outpng)

strips = []
for fn in sorted(os.listdir(CLIPS)):
    if not fn.endswith(".mp4"):
        continue
    clip = os.path.join(CLIPS, fn)
    dur = 5.0
    try:
        p = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
                           capture_output=True, text=True, creationflags=NO_WINDOW, timeout=60)
        dur = float(p.stdout.strip())
    except Exception:
        pass
    frames = []
    for i, t in enumerate([0.4, dur / 2.0, max(0.2, dur - 0.4)]):
        fp = os.path.join(TMP, "%s_%d.png" % (fn[:-4], i))
        if ff(clip, t, fp):
            frames.append(fp)
    if len(frames) < 2:
        continue
    ims = [Image.open(f).convert("RGB").resize((448, 256)) for f in frames]
    W, H, GAP, LBL = 448, 256, 6, 18
    board = Image.new("RGB", (len(ims) * (W + GAP) + GAP, H + LBL + GAP * 2), (24, 22, 20))
    dr = ImageDraw.Draw(board)
    for i, im in enumerate(ims):
        x = GAP + i * (W + GAP)
        board.paste(im, (x, GAP))
    dr.text((GAP, GAP + H + 2), "%s  [t=0.4 / %.1f / %.1f]" % (fn[:-4], dur / 2.0, max(0.2, dur - 0.4)),
            fill=(210, 190, 150))
    strips.append((fn, board))

COLS = 2
SW = max(b.size[0] for _, b in strips) + 10
SH = max(b.size[1] for _, b in strips) + 8
rows = (len(strips) + COLS - 1) // COLS
grid = Image.new("RGB", (COLS * SW + 10, rows * SH + 10), (18, 16, 15))
for i, (fn, b) in enumerate(strips):
    grid.paste(b, (10 + (i % COLS) * SW, 10 + (i // COLS) * SH))
grid.save(OUT, quality=88)
print("STRIPS DONE: %d clips -> %s" % (len(strips), OUT))
