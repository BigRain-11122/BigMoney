# r828 bm-b: append T20 candidate row to tech.md queue (UTF-8 LF, byte-safe)
p = r"state\queue\tech.md"
raw = open(p, "rb").read().decode("utf-8")
assert "| T20 |" not in raw
anchor = "\n\n> r805 消耗记录"
assert anchor in raw
row = (
    "| T20 | update_futures raw fallback OI 键位坑（fetch_raw 把 OI 读自键 \"o\"=开盘价·"
    "真键=\"p\" 持仓量——akshare 主径不受影响·本地面板九品种 OI 全健康〔RB 2026-10-09 "
    "OI=1,673,458 与 per-contract RB2701 逐位恒等〕=latent 仅 akshare 败退 raw 退路才触发；"
    "E8 预检探针实证=results/_r828bmb_e8_shape_probe.py〔5/5 族键位实录〕；lane=bm-a "
    "R48/R51 归属·bm-b 登记不越道修） | scripts/update_futures.py"
    "+research/digests/DIGEST-20261010-e8-futures-calendar-spread.md §一 | open |"
)
new = raw.replace(anchor, "\n" + row + anchor, 1)
open(p, "wb").write(new.encode("utf-8"))
print("T20 row inserted; new bytes:", len(new.encode("utf-8")))
