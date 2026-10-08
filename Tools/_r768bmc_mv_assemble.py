# -*- coding: utf-8 -*-
"""r768 bm-c: MV-0001 20s sample final assembly (O-20261008-1715/1755-bm-c).
Single-re-encode FFmpeg graph:
  6 Wan2.2 i2v segments (832x480 24fps h264) -> per-window trim at
  structure.json word-line starts (77/80/84/88/92/95 -> sample-relative
  0/3/7/11/15/18) -> concat -> scale 1280x720 -> 落点C grading chain
  VERBATIM (R-20261008-mv-craft-deep-01 落点C, ffmpeg-tested exit 0):
  分频三带 colorbalance (mid R-B target +126 calibration) + blue-mute
  colorchannelmixer bb=0.60 + 2383-shape master S-curve -> halation
  subchain (highlight-gate curves + gblur sigma14 + warm colorbalance +
  screen blend) -> gray-base softlight grain 0.45 (alls=30 t+u) ->
  vignette PI/4.6 dither=1 -> 2.35:1 letterbox (crop 546 @y87 + pad
  720) -> subtitles (ASS, canon YaHei 46 warm-cream style) + AIGC mark
  (ASS bottom-left standing event, avoids CJK-on-cmdline mojibake face).
Order law (落点C): 调色->halation->颗粒->暗角->遮幅->字幕. 24fps direct
(no interpolation - 掉帧律: only slow-mo segments get RIFE, none here).
Audio = mv001_source_320k.mp3 window 77.0-97.0 -> aac 192k.
Output: results/mv_work/MV0001_爱在西元前_20s样片_v1.mp4 (720P, 20.0s)."""
import os
import subprocess
import sys

WORK = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work"
SEG = os.path.join(WORK, "seg")
MP3 = os.path.join(WORK, "mv001_source_320k.mp3")
ASS = os.path.join(WORK, "sample20.ass")
OUT = os.path.join(WORK, "MV0001_爱在西元前_20s样片_v1.mp4")

# (segment file, window duration s) - cut points = word-window line starts
WINDOWS = [
    ("seg1_carve_77_80.mp4", 3.0),
    ("seg2_strata_80_84.mp4", 4.0),
    ("seg3_unearth_84_88.mp4", 4.0),
    ("seg4_palms_88_92.mp4", 4.0),
    ("seg5_carve_reprice_92_95.mp4", 3.0),
    ("seg6_strata_reprice_95_97.mp4", 2.0),
]

LYRICS = [
    (0.0, 3.0, "我给你的爱写在西元前"),
    (3.0, 7.0, "深埋在美索不达米亚平原"),
    (7.0, 11.0, "几十个世纪后出土发现"),
    (11.0, 15.0, "泥板上的字迹依然清晰可见"),
    (15.0, 18.0, "我给你的爱写在西元前"),
    (18.0, 20.0, "深埋在美索不达米亚平原"),
]


def ts(sec):
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = sec % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def build_ass():
    rows = [
        "[Script Info]", "ScriptType: v4.00+",
        "PlayResX: 1280", "PlayResY: 720",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Def,Microsoft YaHei,46,&H00F2E8DC,&H00FFFFFF,&H00101010,"
        "&H80000000,-1,1,2,1,2,60,60,44,1",
        "Style: Mark,Microsoft YaHei,24,&H0096C8A0,&H00FFFFFF,&H00101010,"
        "&H80000000,-1,1,1,1,1,36,60,20,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
        "Dialogue: 0,%s,%s,Mark,,0,0,0,,AI 生成 · 改编致敬" % (ts(0.0),
                                                                 ts(20.0)),
    ]
    for a, b, t in LYRICS:
        rows.append("Dialogue: 0,%s,%s,Def,,0,0,0,,%s" % (ts(a), ts(b), t))
    with open(ASS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
    return len(LYRICS) + 1


def main():
    for name, _ in WINDOWS:
        p = os.path.join(SEG, name)
        if not (os.path.exists(p) and os.path.getsize(p) > 10000):
            print("MISSING SEGMENT:", p)
            return 1
    n = build_ass()
    print("ass events:", n)
    trims = "".join(
        "[%d:v]trim=duration=%.1f,setpts=PTS-STARTPTS[s%d];" % (i, d, i)
        for i, (_, d) in enumerate(WINDOWS))
    cat = "".join("[s%d]" % i for i in range(len(WINDOWS))) + \
        "concat=n=%d:v=1:a=0[cat0];" % len(WINDOWS)
    grade = (
        "[cat0]scale=1280:720:flags=lanczos,format=gbrp,split=2[base][hal];"
        "[hal]curves=all='0/0 0.62/0 0.88/0.55 1/1',"
        "gblur=sigma=14:steps=2,"
        "colorbalance=rm=0.32:gm=0.05:bm=-0.28:rh=0.06:bh=-0.04[halo];"
        "[base]colorbalance=rs=0.12:gs=-0.04:bs=-0.18:rm=0.28:gm=0.04:"
        "bm=-0.32:rh=0.05:gh=0.02:bh=-0.05:pl=1,"
        "colorchannelmixer=bb=0.60,"
        "curves=master='0/0.045 0.3/0.28 0.7/0.78 1/0.98'[graded];"
        "[graded][halo]blend=all_mode=screen:shortest=1[glowed];"
        "[6:v]format=gbrp,noise=alls=30:allf=t+u[grain];"
        "[glowed][grain]blend=all_mode=softlight:all_opacity=0.45[grained];"
        "[grained]vignette=angle=PI/4.6:dither=1,"
        "crop=1280:546:0:87,pad=1280:720:0:87:black,"
        "subtitles='%s':fontsdir='C\\:/Windows/Fonts',"
        "format=yuv420p[vout]" % ASS.replace("\\", "/").replace(":", r"\:"))
    fc = trims + cat + grade
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for name, _ in WINDOWS:
        cmd += ["-i", os.path.join(SEG, name)]
    cmd += ["-f", "lavfi", "-t", "20.0",
            "-i", "color=c=gray:s=1280x720:r=24"]
    cmd += ["-ss", "77.0", "-t", "20.0", "-i", MP3]
    cmd += ["-filter_complex", fc, "-map", "[vout]", "-map", "7:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", OUT]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("FFMPEG_FAIL")
        print(r.stderr[-1500:])
        return 1
    print("PRODUCT DONE:", OUT, os.path.getsize(OUT), "B")
    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", OUT, "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in probe.stderr.splitlines():
        if "Duration" in line or "Stream #" in line:
            print(line.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
