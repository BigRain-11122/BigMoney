# -*- coding: utf-8 -*-
"""r1055 bm-c V5 phase2 harvest QC step 1: min_duration>=5.0 assert (17/17) + INT4 frame extract + female-anchor compare board."""
import json, os, subprocess, io

BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\i2v\v5redo"
THUMB = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\v5redo\_thumbs_p2_r1054"
OUTDIR = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
FF = "ffmpeg"

clips = sorted(f for f in os.listdir(BASE) if f.endswith(".mp4"))
assert len(clips) == 17, "expect 17 clips, found %d" % len(clips)

# 1) duration assert via ffprobe-free ffmpeg -i parse (ffprobe present? use ffprobe if avail)
res = {}
bad = []
for c in clips:
    p = os.path.join(BASE, c)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", p], capture_output=True, text=True)
    try:
        d = float(r.stdout.strip())
    except Exception:
        d = -1.0
    res[c] = d
    if d < 5.0:
        bad.append((c, d))

print("DURATION-ASSERT:", "PASS 17/17" if not bad else "FAIL %r" % bad)
for c in clips:
    print("  %-28s %.2fs" % (c, res[c]))

# 2) INT4 double-contour recheck frames: extract 6 frames evenly
i4 = os.path.join(BASE, "INT4_rubbing_v5.mp4")
i4dir = os.path.join(THUMB, "int4_recheck_r1055")
os.makedirs(i4dir, exist_ok=True)
for k, t in enumerate(["0.5", "1.3", "2.1", "2.9", "3.7", "4.5"]):
    out = os.path.join(i4dir, "int4_f%d.jpg" % k)
    subprocess.run([FF, "-y", "-ss", t, "-i", i4, "-frames:v", "1", "-q:v", "2", out],
                    capture_output=True)
print("INT4 frames:", sorted(os.listdir(i4dir)))

# 3) female-anchor compare board: female-lead shots per V5 shotlist = D03b/E03/R06/E04 (+C01 carver face = male)
fem = ["D03b_direct_gaze_v5.mp4", "E03_gaze_meet_v5.mp4", "R06_museum_verse_v5.mp4", "E04_replay_faces_v5.mp4"]
fdir = os.path.join(THUMB, "femanchor_r1055")
os.makedirs(fdir, exist_ok=True)
for c in fem:
    p = os.path.join(BASE, c)
    tag = c.split("_")[0]
    subprocess.run([FF, "-y", "-ss", "2.5", "-i", p, "-frames:v", "1", "-q:v", "2",
                    os.path.join(fdir, tag + "_mid.jpg")], capture_output=True)

# board: 4 shots x 3 timepoints
from PIL import Image
times = ["0.8", "2.5", "4.2"]
cells = []
for c in fem:
    p = os.path.join(BASE, c)
    tag = c.split("_")[0]
    for j, tm in enumerate(times):
        fp = os.path.join(fdir, "%s_t%d.jpg" % (tag, j))
        subprocess.run([FF, "-y", "-ss", tm, "-i", p, "-frames:v", "1", "-q:v", "2", fp], capture_output=True)
        if os.path.exists(fp):
            cells.append((tag, tm, fp))
W = 480
cols = 3
rows_by_tag = {}
for tag, tm, fp in cells:
    rows_by_tag.setdefault(tag, []).append(fp)
tags = list(rows_by_tag)
Hrow = 270
board = Image.new("RGB", (W * cols, Hrow * len(tags)), (24, 24, 24))
from PIL import ImageDraw
dr = ImageDraw.Draw(board)
for r, tag in enumerate(tags):
    for col, fp in enumerate(rows_by_tag[tag][:cols]):
        im = Image.open(fp)
        im.thumbnail((W - 4, Hrow - 24))
        board.paste(im, (col * W + 2, r * Hrow + 20))
        dr.text((col * W + 8, r * Hrow + 4), "%s t=%s" % (tag, times[col]), fill=(255, 220, 120))
out = os.path.join(OUTDIR, "JAY-V5-CHK-E2-FEMALE-ANCHOR-BOARD-r1055.jpg")
board.save(out, quality=88)
print("FEMALE-ANCHOR BOARD ->", out)

json.dump({"durations": res, "bad": bad, "int4_frames": sorted(os.listdir(i4dir)),
           "fem_board": out, "clips": clips},
          io.open(os.path.join(OUTDIR, "QC-v5redo-harvest-r1055-step1.json"), "w"), indent=1)
print("STEP1 DONE")
