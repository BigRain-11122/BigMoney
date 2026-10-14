# -*- coding: utf-8 -*-
# _r1010bmc_wave2_board.py -- board-only leg (harvest phase-4 standalone):
# delivery face already verified 39/39 by wave2_delivery_final_verify_r1010.json
# (dead r1010 window ran manual repair path instead of full harvest script, board never built).
# Builds q88 contact sheet from the 39 local mp4s (mid-frame @2.5s, 7-col grid).
import json, os, subprocess, time

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
BMC = os.path.join(HERE, "bmc")
I2V = os.path.join(BMC, "i2v")
PROG = os.path.join(BMC, "wave2_r998_progress.json")
BOARD = os.path.join(BMC, "wave2_qc_sheet_r1010.jpg")

prog = json.load(open(PROG, encoding="utf-8"))["shots"]
sids = sorted(k for k, v in prog.items() if isinstance(v, dict) and v.get("status") == "SAVED")
print("slots:", len(sids))
assert len(sids) == 39, "expected 39 SAVED"

from PIL import Image, ImageDraw
cols, tw, th, pad = 7, 266, 150, 14
rows_n = (len(sids) + cols - 1) // cols
W = cols * (tw + pad) + pad
H = rows_n * (th + 22 + pad) + pad + 30
board = Image.new("RGB", (W, H), (18, 16, 14))
d = ImageDraw.Draw(board)
d.text((pad, 6), "wave2 harvest 39/39 byte-verified -- r1010 bm-c -- %s" % time.strftime("%Y-%m-%dT%H:%M:%S"), fill=(240, 200, 120))
tmpd = os.path.join(BMC, "_thumb_tmp_r1010")
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
