# r402 post-round addendum append (byte face, LF) + CODELY size water-level check
ROOT = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
addendum = (
    "\n"
    "**POST-ROUND ADDENDUM（r402 送达回执）**：本地未达 origin commit 数=**0**"
    "（push 74a94c056 一发直达 9da5d21a9..74a94c056——途中撞三机高频竞态窗：commit 后 origin 再前进 1 笔"
    "（6268d5dff→9da5d21a9）→pull --rebase 15 冲突全=共享派生聚合面 origin 侧让路"
    "（r400 律·日再生幂等件零科学损失·lane 件/仪器/票/坑律件全保全）→rebase --continue 哑终端 EDITOR 坑"
    "（r505 族）-c core.editor=true 一次治愈→51 件 1487/490 重落直达；fetch+rev-parse behind 0"
    "+ls-tree 七关键件 origin 在场断言：dualrun 仪器 ba28d4ef5/T-147 ef6b87ae0/pit-git d7896a1cc/"
    "pit-pool 5e8c8ca8a/MSG-0725/round_reports/state-bm-c 全验）。S7：loop task pin=5 幂等 no-op"
    "（下轮 07:55:00 首发在册）+watchdog 在位 07:47 跑面+双爪 CR 归一 MATCH+收尾双扫 fetch 零新令"
    "（151/151 维持）。\n"
)
rp = ROOT + "/round_reports-bm-c.md"
with open(rp, "rb") as f:
    tail = f.read()
assert tail.endswith(b"\n")
with open(rp, "ab") as f:
    f.write(addendum.encode("utf-8"))
with open(rp, "rb") as f:
    assert f.read() == tail + addendum.encode("utf-8"), "append not byte-clean"
import os
sz = os.path.getsize(ROOT + "/CODELY.md")
print(f"ADDENDUM OK; CODELY.md size = {sz}B ({'OVER' if sz > 51200 else 'under'} 50KB line)")
