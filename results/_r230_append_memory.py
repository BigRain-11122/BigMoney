import io

APPEND = (" - [2026-09-26 07:0x] 坑律（bm-b r230·P1E_SYNTH runner 交付·自检夹具新维·r157/r221 灰度补篇）："
          "**含 IS/OOS 分段逻辑（IS_END=2024-12-31）的自检夹具日历必须跨 IS_END——照母批同子面板抄 T=300 小夹具停 2020-2021：OOS 段空=stats_block 无 ic_mean 键，锚腿 KeyError 自捕；正例=夹具日历 2018 起 T=2600 双段非空**；"
          "连带 **DataFrame.any()/.max() 标量陷阱——聚合值是 per-column Series，bool() 即崩；一律 .any().any()/.max().max() 同款记面（p1e_synth selftest [2/9] 三连小翻车实证）**；"
          "另一记面=PowerShell 会话层 GBK 乱码复制进 Add-Content=写入即损（U+FFFD 落盘自捕）——CODELY 追加一律 python 直写 UTF-8 禁 PS 字符串中转。"
          "指针=scripts/p1e_synth.py _synth_panels 注记+selftest [2/9] 夹具。\n")

with open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write(APPEND)
raw = open("CODELY.md", encoding="utf-8").read()
assert "\ufffd" not in raw[-500:], "replacement char leaked"
lines = raw.rstrip("\n").split("\n")
print("appended ok, size:", len(raw.encode("utf-8")), "bytes")
print("tail head:", lines[-1][:60])
