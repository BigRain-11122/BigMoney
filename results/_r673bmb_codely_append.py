import io

P = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
entry = (
    "- [2026-10-04 13:4x r673 bm-b] daemon treadmill 下批量 UU 收口 add 一律单次调用整清单"
    "（ForEach 逐件 git add=31 个锁窗口，13:37 撞 autofill self-commit tick 的 index.lock 瞬态"
    "（fatal Unable to create index.lock·30/31 已入后中断·commit 假报 unresolved 拒绝），单次"
    " git add <全部路径> 重试即收=1 个锁窗口零竞态；锁消失后按 porcelain UU 余量定点补 add 再 commit。"
    "How to apply：收口脚本产 UU 清单后用一条 git add 命令带全路径，禁 ForEach 循环逐件 add。\n"
)
with io.open(P, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
t = io.open(P, encoding="utf-8", errors="replace").read()
assert t.count("ForEach 逐件 git add") == 1
import os
print("appended; size=%d" % os.path.getsize(P))
