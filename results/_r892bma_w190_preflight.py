# -*- coding: utf-8 -*-
"""r892 bm-a pre-flight: extract the freeze-time W189 prereg blob (LF,
byte-verbatim) to results/_r892bma_w190_prereg_src.txt and count-check
the planned S87 (W189->W190) fact-map old sides against the physical src.
Read-only for the repo tree (writes only the src extract + prints).
Two-face law (r881/r885/r888/r890 bloodline): build src = the FREEZE face
(blob at prereg-freeze commit 632761894 == five-face-registration commit
8addea3eb), NOT the current post-backfill FINAL face (the r892 backfill
landed this window -- sec7/sec8 regions would leak W189 actuals)."""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "735f7c288539d58a181cacab9b9335fc632e7a33", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "8addea3eb:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registration blob"
blob = subprocess.run(
    ["git", "show", "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
open(r"results/_r892bma_w190_prereg_src.txt", "wb").write(blob)
src = blob.decode("utf-8")
print("src bytes:", len(blob), "blob", BLOB_SHA[:10])

# current face = post-backfill FINAL (this window, r892 first leg)
_cur = io.open(r"research/PERPETUAL_N1_W189_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
assert b"r892" in _cur, "backfill window stamp missing on current face"

# planned S87 old sides (session composites / bands / ordinals / numbers)
S87_OLDS = [
    # session composites
    "已回填（r890 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W182 拖延窗先例对照·如实注记）",
    "已回填（r890 回填窗）",
    "r888 bm-a 带闸窗（pre-seat probe r888 单窗",
    "（r890 承袭",
    "r888 probe 单跑兑现注记",
    "（r888 probe leg2/leg3 实跑）",
    "r888 probe 回执 A_semantics 机读序数=FORTY-NINTH",
    "FORTY-NINTH（第四十九例）",
    "r888 probe leg4",
    "（r888 冻结件）",
    "_r888bma_w189_probe_receipt.json",
    "MSG-2026-10-08-1815-bma-w189-seat",
    "744de26ef",
    "【r890】",
    "r888 seat push",
    "自 r888 收口",
    "bm-a r889 窗归档",
    "本机 r888 席位",
    "（r888 seat push·r565 律）",
    # bands
    "432_604..434_603", "432_804..433_003", "432_604..432_803",
    "430_604..432_603", "430_404..430_603", "430_404..432_403",
    "430_604..430_803", "432_603+1", "430_603+1", "430_604+j", "432_604+j",
    # ordinals
    "第五十例", "第四十九例", "第 187 枚", "行 178+本候选", "第一百零五枚",
    "第 179 波", "行 104+本候选", "bm-a 104 行注册", "一百八十六行注册",
    "机证 186 行", "一百八十七面实测",
    # n1_w forms
    "n1_w189", "n1_w188",
    # numbers
    "**413,720 投影**", "**1.1862**", "**+0.0000**【line_merged",
    "**0.3243**", "**\u22120.0825**", "**\u22120.0986**", "0.245115",
    "line_pre 1.1862", "820,928", "818,728", "411,520",
    # bare wave numbers
    "波号 189=", "--wave 189",
    # wave-word cascade lows
    "W183", "W182",
]
for old in S87_OLDS:
    print("%3d  %s" % (src.count(old), old[:72]))

# session-string census for the DRY gate design
print("\n-- session census in src --")
for s in ("r885", "r886", "r888", "r889", "r890", "r891", "r892",
          "r844", "r839"):
    print("%3d  %s" % (src.count(s), s))
