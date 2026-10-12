# r955 R05_gold_threads_v2 QC: v1 failed on light drift (brightness ramp ~2 stops)
# + gold thread form loss (edge line -> whole-groove fill). v2 fix prompt pinned
# light level + thread form. Extract 6 spread frames + dense 0.2s strip for
# light-stability and thread-form verification.
import subprocess, os
from PIL import Image, ImageDraw

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
ARC = os.path.join(BMC, "archive_i2v")
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
FRAMES = os.path.join(OUT, "_r955bmc_qcframes")
os.makedirs(FRAMES, exist_ok=True)

TAG = "R05_gold_threads_v2"
SPREAD = [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]
DENSE = [round(0.6 + 0.4 * i, 2) for i in range(11)]  # 0.6..4.6 @0.4s

def extract(tag, ts, suffix="f"):
    src = os.path.join(ARC, tag + ".mp4")
    dst = os.path.join(FRAMES, "%s_%s%d.png" % (tag, suffix, ts * 10))
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
    W = max(len(p) for _, p, _ in rows) * CW
    H = sum(len(p) * (CH + LBL) + 30 for _, p, _ in rows)
    img = Image.new("RGB", (W, H), (24, 24, 24))
    d = ImageDraw.Draw(img)
    y = 0
    for tag, paths, sfx in rows:
        d.text((6, y + 4), "== %s ==" % tag, fill=(255, 210, 80))
        y += 26
        for p in paths:
            fr = Image.open(p).convert("RGB")
            fr.thumbnail((CW, CH))
            t = int(os.path.basename(p).rsplit("_%s" % sfx, 1)[1].split(".")[0]) / 10.0
            d.text((6, y + 4), "t=%.1fs" % t, fill=(120, 220, 120))
            y += LBL
            img.paste(fr, (0, y))
            y += fr.size[1]
        y += 4
    out = os.path.join(OUT, name)
    img.save(out, quality=88)
    print("SHEET", out, img.size)

spread = [extract(TAG, t, "f") for t in SPREAD]
dense = [extract(TAG, t, "d") for t in DENSE]
sheet("_r955bmc_r05v2_sheet.png", [(TAG + " spread", spread, "f"),
                                   (TAG + " dense", dense, "d")])
print("DONE", len(spread), "spread +", len(dense), "dense")
