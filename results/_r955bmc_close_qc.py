# r955 QC finish (dead-session estate absorb): extract 5 missing clips + build 3 sheets.
# Estate reuse: C03_v2/C09_v2/R05_v2/R06/B01/E03 frames already extracted by dead r955 session.
# This script adds: C04_words_alive_v2 (new track2 frame, landed 05:49), R02_she_turns_v3 (05:56),
# C07_stele_sink_v3 (06:04), INT2v1_s9026 (i2v/ 05:20), INT4v2_s9030 (i2v/ 05:34).
import subprocess, os
from PIL import Image, ImageDraw

BMC = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"
ARC = os.path.join(BMC, "archive_i2v")
I2V = os.path.join(BMC, "i2v")
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
FRAMES = os.path.join(OUT, "_r955bmc_qcframes")
os.makedirs(FRAMES, exist_ok=True)

def src_for(tag):
    for d in (ARC, I2V):
        p = os.path.join(d, tag + ".mp4")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(tag)

def extract(tag, ts):
    dst = os.path.join(FRAMES, "%s_f%d.png" % (tag, ts * 10))
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        return dst
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ts), "-i", src_for(tag),
                        "-frames:v", "1", "-q:v", "2", dst], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dst):
        print("EXTRACT_FAIL", tag, ts, r.stderr[:200]); raise SystemExit(2)
    return dst

SPREAD = [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]

def sheet(name, rows):
    # rows: list of (label, [6 frame paths])
    CW, CH, LBL = 480, 270, 22
    W = 6 * CW
    H = len(rows) * (CH + LBL)
    img = Image.new("RGB", (W, H), (18, 18, 18))
    d = ImageDraw.Draw(img)
    y = 0
    for label, paths in rows:
        d.text((8, y + 4), label, fill=(255, 210, 120))
        y += LBL
        x = 0
        for p in paths:
            f = Image.open(p).convert("RGB")
            f.thumbnail((CW, CH))
            img.paste(f, (x, y))
            d.rectangle([x, y, x + CW, y + CH], outline=(70, 70, 70))
            x += CW
        y += CH
    outp = os.path.join(OUT, name)
    img.save(outp, "PNG")
    print("SHEET", outp, img.size)
    return outp

def row(tag):
    return (tag, [extract(tag, t) for t in SPREAD])

if __name__ == "__main__":
    s1 = sheet("_r955bmc_close_sheet_track2.png", [
        row("C03_dig_reveal_v2"),
        row("C04_words_alive_v2"),
        row("C09_oath_weather_v2"),
    ])
    s2 = sheet("_r955bmc_close_sheet_reshake.png", [
        row("R02_she_turns_v3"),
        row("C07_stele_sink_v3"),
        row("R05_gold_threads_v2"),
    ])
    s3 = sheet("_r955bmc_close_sheet_rest.png", [
        row("R06_museum_verse"),
        row("B01_weary"),
        row("E03_gaze_meet"),
        row("INT2v1_s9026"),
        row("INT4v2_s9030"),
    ])
    print("DONE 3 sheets")
