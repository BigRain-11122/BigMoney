# r955 C09_oath_weather_v2 QC: track-2 regen frame i2v (landed 05:27).
# Two-person side-profile oath + bronze brazier + meander wall <=30% frame.
# bm-a frame QC 9/10 disclosed: fire small, thin dust weak (i2v should add wind).
import subprocess, os
from PIL import Image, ImageDraw

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
ARC = os.path.join(BMC, "archive_i2v")
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
FRAMES = os.path.join(OUT, "_r955bmc_qcframes")
os.makedirs(FRAMES, exist_ok=True)

TAG = "C09_oath_weather_v2"
SPREAD = [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]

def extract(tag, ts):
    src = os.path.join(ARC, tag + ".mp4")
    dst = os.path.join(FRAMES, "%s_f%d.png" % (tag, ts * 10))
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        return dst
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts), "-i", src,
                        "-frames:v", "1", "-q:v", "2", dst],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dst):
        print("EXTRACT_FAIL", tag, ts, r.stderr[:200]); raise SystemExit(2)
    return dst

def sheet(name, rows):
    CW, CH, LBL = 480, 270, 22
    W = max(len(p) for _, p in rows) * CW
    H = sum(len(p) * (CH + LBL) + 30 for _, p in rows)
    img = Image.new("RGB", (W, H), (24, 24, 24))
    d = ImageDraw.Draw(img)
    y = 0
    for tag, paths in rows:
        d.text((6, y + 4), "== %s ==" % tag, fill=(255, 210, 80))
        y += 26
        for p in paths:
            fr = Image.open(p).convert("RGB")
            fr.thumbnail((CW, CH))
            t = float(os.path.basename(p).rsplit("_f", 1)[1].split(".")[0]) / 10.0
            d.text((6, y + 4), "t=%.1fs" % t, fill=(120, 220, 120))
            y += LBL
            img.paste(fr, (0, y))
            y += fr.size[1]
        y += 4
    out = os.path.join(OUT, name)
    img.save(out, quality=88)
    print("SHEET", out, img.size)

spread = [extract(TAG, t) for t in SPREAD]
sheet("_r955bmc_c09v2_sheet.png", [(TAG, spread)])
print("DONE", len(spread), "frames")
