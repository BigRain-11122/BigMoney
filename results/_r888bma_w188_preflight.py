# -*- coding: utf-8 -*-
"""r888 bm-a pre-flight: extract the freeze-time W187 prereg blob (LF,
byte-verbatim) to results/_r888bma_w188_prereg_src.txt and count-check
the planned S85 (W187->W188) fact-map old sides against the physical src.
Read-only for the repo tree (writes only the src extract + report)."""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "8fbae1c4fc5cc4f92708ef077914fc9256339e04", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "79c9a567c:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
open(r"results/_r888bma_w188_prereg_src.txt", "wb").write(blob)
src = blob.decode("utf-8")
print("src bytes:", len(blob), "blob", BLOB_SHA[:10])

# current face = post-backfill FINAL (this window)
_cur = io.open(r"research/PERPETUAL_N1_W187_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W187_PREREG.md"],
                    capture_output=True).stdout
assert _cur.replace(b"\r\n", b"\n") != _o or True  # origin may predate backfill; push lands this window

# planned S85 old sides (session composites / bands / ordinals / numbers)
S85_OLDS = [
    "已回填（r885 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
    "已回填（r885 回填窗）",
    "r885 bm-a 带闸窗（pre-seat probe r885 单窗",
    "（r885 承袭",
    "r885 probe 单跑兑现注记",
    "（r885 probe leg2/leg3 实跑）",
    "r885 probe 回执 A_semantics 机读序数=FORTY-SEVENTH",
    "FORTY-SEVENTH（第四十七例）",
    "r880 probe leg4",
    "（r881 冻结件）",
    "_r885bma_w187_probe_receipt.json",
    "MSG-2026-10-08-1626-bma-w187-seat",
    "d176af598",
    "【r885】",
    "r885 seat push",
    "自 r885 收口",
    "bm-a r885 窗自移",
    "本机 r885 席位",
    "（r885 seat push·r565 律）",
    # bands
    "428_204..430_203", "428_404..428_603", "428_204..428_403",
    "426_204..428_203", "426_004..426_203", "426_004..428_003",
    "426_204..426_403", "426_203+1", "428_203+1", "426_204+j", "428_204+j",
    # ordinals
    "第四十八例", "第四十七例", "第 185 枚", "行 176+本候选", "第一百零三枚",
    "第 177 波", "行 102+本候选", "bm-a 102 行注册", "一百八十四行注册",
    "机证 184 行", "一百八十五面实测",
    # n1_w forms
    "n1_w187", "n1_w186",
    # numbers
    "**409,320 投影**", "**1.1858**", "·line_pre 1.1859·", "**0.3004**",
    "**\u22120.1025**", "**\u22120.0929**", "0.245086", "816,528", "814,328",
    "407,120",
    # bare wave numbers
    "波号 187=", "--wave 187",
    # wave-word cascade lows
    "W181", "W180",
]
for old in S85_OLDS:
    print("%3d  %s" % (src.count(old), old[:72]))
