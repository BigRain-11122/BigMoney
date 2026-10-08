# -*- coding: utf-8 -*-
"""r890 bm-a pre-flight: extract the freeze-time W188 prereg blob (LF,
byte-verbatim) to results/_r890bma_w189_prereg_src.txt and count-check
the planned S86 (W188->W189) fact-map old sides against the physical src.
Read-only for the repo tree (writes only the src extract + prints)."""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "b66117659:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "b2608fe43e9d51553a4a2ef4203342f2f787af5a", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "edec49746:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "b66117659:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
open(r"results/_r890bma_w189_prereg_src.txt", "wb").write(blob)
src = blob.decode("utf-8")
print("src bytes:", len(blob), "blob", BLOB_SHA[:10])

# current face = post-backfill FINAL (this window)
_cur = io.open(r"research/PERPETUAL_N1_W188_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"

# planned S86 old sides (session composites / bands / ordinals / numbers)
S86_OLDS = [
    # session composites
    "已回填（r888 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
    "已回填（r888 回填窗）",
    "r887 bm-a 带闸窗（pre-seat probe r887 单窗",
    "（r888 承袭",
    "r887 probe 单跑兑现注记",
    "（r887 probe leg2/leg3 实跑）",
    "r887 probe 回执 A_semantics 机读序数=FORTY-EIGHTH",
    "FORTY-EIGHTH（第四十八例）",
    "r885 probe leg4",
    "（r885 冻结件）",
    "_r887bma_w188_probe_receipt.json",
    "MSG-2026-10-08-1717-bma-w188-seat",
    "943967370",
    "【r888】",
    "r887 seat push",
    "自 r887 收口",
    "bm-a r887 窗自移",
    "本机 r887 席位",
    "（r887 seat push·r565 律）",
    # bands
    "430_404..432_403", "430_604..430_803", "430_404..430_603",
    "428_404..430_403", "428_204..428_403", "428_204..430_203",
    "428_404..428_603", "428_403+1", "430_403+1", "428_404+j", "430_404+j",
    # ordinals
    "第四十九例", "第四十八例", "第 186 枚", "行 177+本候选", "第一百零四枚",
    "第 178 波", "行 103+本候选", "bm-a 103 行注册", "一百八十六行注册",
    "机证 186 行", "一百八十六面实测",
    # n1_w forms
    "n1_w188", "n1_w187",
    # numbers
    "**411,520 投影**", "**1.1861**", "**+0.0002**【line_merged",
    "**0.339**", "**\u22120.0825**", "**\u22120.0928**", "0.245086",
    "818,728", "816,528", "409,320",
    # line_pre display (rolls this generation)
    "line_pre 1.1859",
    # bare wave numbers
    "波号 188=", "--wave 188",
    # wave-word cascade lows
    "W181", "W180",
]
for old in S86_OLDS:
    print("%3d  %s" % (src.count(old), old[:72]))

# session-string census for the DRY gate design
print("\n-- session census in src --")
for s in ("r885", "r887", "r888", "r889", "r890", "r880", "r875", "r841",
          "r844", "r839"):
    print("%3d  %s" % (src.count(s), s))
