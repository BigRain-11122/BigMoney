# r389 bm-a: CODELY hot-cold rework batch-33 (watermark law: append -> over 10KB line -> same-window fold)
# Moves r363 + r386 pit entries verbatim to research/memory-archive/202609.md batch-33 section,
# appends the new r389 auto-clear x lane-union pit entry to the hot layer.
# Zero-loss verification: per-line verbatim containment in archive + absence in hot + size gate.
import io

NEW = ("- [2026-09-28 07:1x r389 bm-a] \u5751\u5f8b\uff1a**tick auto-clear\uff08\u7801\u53d8\u2192del sig\u2192_save_fuse \u53cc\u8f68\u5199\uff09\u00d7 lane-union \u9762=shared \u843d\u540e\u6ce8\u518c\u673a lane \u7684 reconcile \u6f02\u79fb**"
       "\uff08r389 \u5b9e\u5f39\uff1a07:00:01 tick cbe4792f \u6e05 bm-c 06:50:03 \u6ce8\u518c\u7684 trial_labor_w2 \u65e7\u7801 sig\u2192shared 2 sigs vs lane union 3 sigs=reconcile \u65d7\u6f02\u79fb\uff1b"
       "done \u6761\u76ee\u4e0d\u518d\u88ab pick=\u65e0\u518d\u6e05\u975e\u6d3b\u9501\uff0c\u6062\u590d shared:=canon union\uff08face_view \u4ea7\u51fa\u7981\u624b\u62fc r376\uff09\u5373\u5168\u7eff\u6536\u655b\uff09\u3002"
       "How to apply\uff1a\u2460auto-clear \u6f02\u79fb=\u5df2\u77e5\u826f\u6027\u7c7b\uff0c\u6062\u590d\u4e00\u5f8b merge_lane_views.face_view \u5199\u56de\uff1b"
       "\u2461\u6839\u6027\u89e3=D-03(2) \u8bbe\u8ba1\u7247\uff08cleared-tombstone/owner-clear \u8bed\u4e49\u5165 merge_crash_fuse\uff09\u672a\u51b3\u524d\u4ee5\u6062\u590d\u6536\u655b\u4e3a\u8fc7\u6e21\u914d\u65b9\u3002"
       "\u6307\u9488=round_reports-bm-a R389 addendum+cbe4792f diff\u3002")

TARGETS = ["- [2026-09-28 06:4x r363 bm-b] \u5751\u5f8b\uff1a",
           "- [2026-09-28 06:3x r386 bm-a] \u5751\u5f8b\uff1a"]

hot_p = "CODELY.md"
arc_p = "research/memory-archive/202609.md"

hot_raw = open(hot_p, "rb").read().decode("utf-8")
arc_raw = open(arc_p, "rb").read().decode("utf-8")
hot_lines = hot_raw.split("\r\n")

# 1) append new entry to hot tail (preserve trailing blank structure)
assert hot_lines[-1] == "", "hot file must end with blank (CRLF trailing)"
hot_lines.insert(len(hot_lines) - 1, NEW)

# 2) extract + remove target entries (entry line + one adjacent blank)
moved = []
for pref in TARGETS:
    idx = [i for i, l in enumerate(hot_lines) if l.startswith(pref)]
    assert len(idx) == 1, f"target not unique: {pref} -> {idx}"
    i = idx[0]
    moved.append(hot_lines[i])
    if i > 0 and hot_lines[i - 1] == "":
        del hot_lines[i - 1:i + 1]
    elif i + 1 < len(hot_lines) and hot_lines[i + 1] == "":
        del hot_lines[i:i + 2]
    else:
        del hot_lines[i]

hot_new = "\r\n".join(hot_lines)
arc_add = ("\r\n\r\n## \u5751\u5f8b\u5f52\u6863 2026-09-28 \u4e09\u5341\u4e09\u6279\uff08r389 bm-a \u7a97\u00b7\u6c34\u4f4d\u5f8b\u5f53\u7a97\u6574\u7f16\uff1a\u65b0\u5751\u5f8b append \u540e\u8d85 \u226410KB \u786c\u7ebf\uff09\r\n\r\n"
           + moved[0] + "\r\n\r\n" + moved[1]
           + "\r\n\r\n> \u8fc1\u79fb\u8bb0\u5f55\uff08\u4e09\u5341\u4e09\u6279=\u4e24\u6761\u5751\u5f8b r363 \u771f\u6570\u636e\u9996\u8dd1\u8fde\u73af\u649e/r386 hermetic \u65f6\u95f4\u63a8\u8fdb\u96f6\u8986\u76d6\uff0c\u81ea CODELY.md \u70ed\u5c42 verbatim \u8fc1\u79fb\u3014\u884c\u7ea7\u96f6\u4e22\u5931\u6821\u9a8c\u3015\uff1b\u70ed\u5c42\u542b\u4e09\u5341\u4e09\u6279\u6307\u9488\u884c\u3014\u5f52\u6863\u4fa7\u8fc1\u79fb\u53f2\u7559\u75d5\u3015\u3002\r\n")
arc_new = arc_raw.rstrip("\r\n") + arc_add + "\r\n"

# 3) zero-loss verification BEFORE write
for m in moved:
    assert m in arc_new, "moved entry not verbatim in archive"
    assert m not in hot_new, "moved entry still in hot"

open(hot_p, "wb").write(hot_new.encode("utf-8"))
open(arc_p, "wb").write(arc_new.encode("utf-8"))

import os
hs = os.path.getsize(hot_p)
print("moved:", [m[:48] for m in moved])
print("hot size:", hs, "<=10240:", hs <= 10240)
# re-verify from disk
h2 = open(hot_p, "rb").read().decode("utf-8")
a2 = open(arc_p, "rb").read().decode("utf-8")
for m in moved:
    assert m in a2 and m not in h2
assert NEW in h2
print("zero-loss disk re-verify: PASS")
