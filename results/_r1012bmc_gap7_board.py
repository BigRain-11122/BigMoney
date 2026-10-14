# -*- coding: utf-8 -*-
# _r1012bmc_gap7_board.py -- POOL-0012 gap7 harvest board leg:
# q88 contact sheet from the 7 delivered gap7 mp4s (mid-frame @2.5s, 4-col grid).
import json, os, subprocess, time

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
BMC = os.path.join(HERE, "bmc")
I2V = os.path.join(BMC, "i2v")
PROG = os.path.join(BMC, "v3gap7_r1011_progress.json")
BOARD = os.path.join(BMC, "v3gap7_qc_sheet_r1012.jpg")

prog = json.load(open(PROG, encoding="utf-8"))["shots"]
sids = sorted(k for k, v in prog.items() if isinstance(v, dict) and v.get("status") == "DELIVERED")
print("slots:", len(sids), sids)
assert len(sids) == 7, "expected 7 DELIVERED"

from PIL import Image, ImageDraw
cols, tw, th, pad = 4, 266, 150, 14
rows_n = (len(sids) + cols - 1) // cols
W = cols * (tw + pad) + pad
H = rows_n * (th + 22 + pad) + pad + 30
board = Image.new("RGB", (W, H), (18, 16, 14))
d = ImageDraw.Draw(board)
d.text((pad, 6), "POOL-0012 V3 gap7 7/7 delivered byte-verified -- r1012 bm-c -- %s" % time.strftime("%Y-%m-%dT%H:%M:%S"), fill=(240, 200, 120))
tmpd = os.path.join(BMC, "_thumb_tmp_r1012")
os.makedirs(tmpd, exist_ok=True)
for i, sid in enumerate(sids):
    r_, c_ = divmod(i, cols)
    x = pad + c_ * (tw + pad)
    y = pad + 30 + r_ * (th + 22 + pad)
    tf = os.path.join(tmpd, sid + ".png")
    if not os.path.isfile(tf):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.5", "-i",
                        os.path.join(I2V, sid + ".mp4"), "-frames:v", "1", "-vf",
                        "scale=%d:%d,setsar=1" % (tw, th), tf], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.isfile(tf):
        try:
            im = Image.open(tf).convert("RGB")
            board.paste(im, (x, y))
        except Exception as ex:
            print("thumb fail", sid, ex)
    d.text((x, y + th + 3), sid, fill=(200, 200, 200))
board.save(BOARD, "JPEG", quality=88)
print("BOARD ->", BOARD, os.path.getsize(BOARD), "bytes")
