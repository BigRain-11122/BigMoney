# -*- coding: utf-8 -*-
# r1038 bm-c: xq T1 tier-1 sea-review board->cell mapping builder (POOL-0015)
# Mirrors runner sort exactly: sorted(x for x in os.listdir(T1DIR) if x.endswith('.png'))
# 24 cells/board, 4 cols, row-major; label under cell = filename minus .png
import json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = r"K:\Fluxgroup\FluxGroup"
ALBUM = os.path.join(GROUP, "cph4", "fleet", "mv-album-001-jay")
T1DIR = os.path.join(GROUP, "media", "MV", "mv0001", "xingqing", "t1")
R = json.load(open(os.path.join(ALBUM, "xq-T1-RECEIPT-r1035.json"), encoding="utf-8"))

# frame -> (seeds, prompt, light)
fr = {}
for f in R["frames"]:
    fr[f["frame"]] = (f["seeds"], f["prompt"], f.get("light_cell", ""))

files = sorted(x for x in os.listdir(T1DIR) if x.endswith(".png"))
assert len(files) == 264, len(files)
PER, COLS = 24, 4
boards = []
for bi in range(0, len(files), PER):
    chunk = files[bi:bi + PER]
    cells = []
    for i, fn in enumerate(chunk):
        stem = fn[:-4]                     # e.g. F0-01a_s20000
        m = re.match(r"^(.+)_s(\d+)$", stem)
        fid, seed = m.group(1), int(m.group(2))
        seeds, prompt, light = fr[fid]
        assert seed in seeds, (fid, seed)
        cells.append({"pos": "r%d c%d" % (i // COLS + 1, i % COLS + 1),
                      "file": stem, "frame": fid, "seed": seed,
                      "light": light, "anchor": prompt})
    boards.append({"board": len(boards) + 1,
                   "jpg": os.path.join(ALBUM, "xq-T1-BOARD-%02d-r1035.jpg" % (len(boards) + 1)),
                   "cells": cells})

out = os.path.join(REPO, "results", "_r1038bmc_xq_t1_tier1_map.json")
json.dump({"boards": boards}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for b in boards:
    frames = []
    for c in b["cells"]:
        if c["frame"] not in frames:
            frames.append(c["frame"])
    print("board %02d: %s | frames=%s" % (b["board"], os.path.basename(b["jpg"]), ",".join(frames)))
print("map ->", out)
