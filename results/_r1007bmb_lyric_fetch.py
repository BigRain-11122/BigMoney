# -*- coding: utf-8 -*-
# r1007 bm-b: extract FULL lyric rows from both pages with fixed boiler filter,
# write clean lyrics/<曲>.txt (v1-batch format) + dump raw page text to files for verification
import io
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
LYR_DIR = r"C:\Fluxgroup\FluxGroup\cph4\fleet\mv-album-001-jay\lyrics"
OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results"
SONGS = {"斗牛": "https://www.lyrics.net.cn/lyrics/24",
         "黑色幽默": "https://www.lyrics.net.cn/lyrics/73487"}

# footer/nav markers only — song-title words REMOVED (they appear inside lyric lines)
NAV_PREFIX = ("查看歌词解读", "返回顶部", "歌词收录登记", "建议与反", "歌词网歌词内容来自互联网",
              "浙ICP", "|", "-->", "/")


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def page_text_lines(html):
    text = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", text)
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


for song, url in SONGS.items():
    html = get(url)
    lines = page_text_lines(html)
    # dump full page text for evidence
    with io.open(OUT + "\\_r1007bmb_lyric_page_%s.txt" % song, "w", encoding="utf-8") as f:
        for i, ln in enumerate(lines):
            f.write("%3d | %s\n" % (i, ln))
    # lyric block = contiguous run between the second standalone song-title/artist header pair
    # robust: find index of line == song title (line 9-ish) and take until NAV_PREFIX hit
    start = None
    for i, ln in enumerate(lines):
        if ln == song and i > 5:
            start = i + 2  # skip title line + artist line
            break
    rows = []
    for ln in lines[start:]:
        if any(ln.startswith(p) or ln == p for p in NAV_PREFIX):
            break
        rows.append(ln)
    print(song, "start=", start, "rows=", len(rows))
    path = LYR_DIR + "\\" + song + ".txt"
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# title=%s\n" % song)
        f.write("# source=%s\n" % url)
        for r in rows:
            f.write(r + "\n")
    print("WROTE", path, "rows=", len(rows))
