# r952 harvest patrol: extract QC frames from 3 landed i2v clips
# C09_oath_weather (factory, landed 03:04) + R01_war_later (factory, 03:12)
# + C02_sand_bury_v4 (rider reshake, 03:19; trajectory v1 5.5 / v2 5.5 / v3 6.4)
# Pattern: r951b framesheet method (PIL contact sheet + multimodal pass)
import subprocess, os, sys
from PIL import Image, ImageDraw

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
ARC = os.path.join(BMC, "archive_i2v")
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
FRAMES = os.path.join(OUT, "_r952bmc_qcframes")
os.makedirs(FRAMES, exist_ok=True)

CLIPS = {
    "C02_sand_bury_v4": [0.5, 1.3, 2.1, 2.9, 3.7, 4.5],  # 6 frames, motion-critical reshake verdict
    "C09_oath_weather": [0.5, 1.3, 2.1, 2.9, 3.7, 4.5],  # 6 frames, dynamic weather
    "R01_war_later":    [0.8, 2.0, 3.2, 4.4],            # 4 frames, reprise wide
}

def extract(tag, ts):
    src = os.path.join(ARC, tag + ".mp4")
    dst = os.path.join(FRAMES, "%s_f%d.png" % (tag, ts * 10))
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        return dst
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts), "-i", src,
                        "-frames:v", "1", "-q:v", "2", dst],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dst):
        print("EXTRACT_FAIL", tag, ts, r.stderr[:200]); sys.exit(2)
    return dst

def sheet(name, rows):
    CW, CH, LBL = 480, 270, 22
    maxcols = max(len(p) for _, p in rows)
    W = maxcols * CW
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

def main():
    paths = {}
    for tag, ts_list in CLIPS.items():
        paths[tag] = [extract(tag, t) for t in ts_list]
    sheet("_r952bmc_qc_sheet1.png", [("C02_sand_bury_v4", paths["C02_sand_bury_v4"])])
    sheet("_r952bmc_qc_sheet2.png", [("C09_oath_weather", paths["C09_oath_weather"]),
                                     ("R01_war_later", paths["R01_war_later"])])
    print("OK 3 clips extracted")

if __name__ == "__main__":
    main()
