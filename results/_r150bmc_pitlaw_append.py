# -*- coding: utf-8 -*-
"""r150 bm-c: append the new pitlaw entry to CODELY.md hot layer
(console-inline Chinese = GBK mojibake trap; file-based append)."""
import io

CODELY = "CODELY.md"
new_entry = (
    "- [2026-09-28 09:0x r150 bm-c] 坑律：**池文件全幅 UU 的冲突界切在 JSON 顶层"
    "对象内部——三段（ours/base/theirs）各缺共享尾的顶层闭括号 `}`，单独解析必"
    " JSONDecodeError；共享尾（`>>>>>>>` 之后）恰为该括号**（r150 实弹："
    "runnable_pool.json 撞 bm-b tick keepalive 整文件冲突，ours 段尾=entries `]` "
    "止、顶层 `}` 在 >>>>>>> 后公共区；误按完整段解析=Expecting ',' delimiter "
    "假象勿据此判侧）。How to apply：解析器按标记行切三段后各补 `\\n}` 才是完整 "
    "JSON；断言共享尾 strip 后恒等 `}`（异样=冲突界形态变体须重判勿套用）；union "
    "后按完整顶层 dict 序列化写回，禁分段拼接。指针=results/_r150bmc_resolve_pool."
    "py（三断言护栏）+commit 5010fc0b。\n")

hot = io.open(CODELY, "r", encoding="utf-8", newline="").read()
assert new_entry.strip() not in hot, "already present"
assert hot.endswith("\n")
hot2 = hot + new_entry
io.open(CODELY, "w", encoding="utf-8", newline="\n").write(hot2)
chk = io.open(CODELY, "r", encoding="utf-8", newline="").read()
assert new_entry.strip() in chk
sz = len(chk.encode("utf-8"))
print(f"appended; hot={sz}B (line 10240: {'UNDER' if sz <= 10240 else 'OVER'})")
