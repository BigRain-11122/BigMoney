# -*- coding: utf-8 -*-
"""r786 bm-a S4: single CODELY.md pit entry append (fresh read-modify-write)."""
import io

CP = r"CODELY.md"
t = io.open(CP, encoding="utf-8", newline="").read()
nl = "\r\n" if t.endswith("\r\n") else "\n"

entry = ("- [2026-10-06 17:4x r786 bm-a] **D-19 水位探针本地面哈希坑（r785 dec 512dc730 实弹·bm-c MSG-1735 "
         "跨机哨捕获·r786 同窗定谳零消费伤害）**：git show origin/main:docs/decisions.md 是正典读法（法已在 "
         "prompt），但 r785 实窗产出键 512dc730 非 origin blob——origin tip 85c61c5 自 13:47 未动=时间戳考古证"
         "本地面（工作树脏读/本地 patrol commit 面）；危害=键错位后未来真新增行会被「已消费」假象掩蔽。姊妹坑="
         "跨机水位键比对未标哈希算法（bm-c SHA-1 36B2594C vs 本机 SHA-256 3e8c73e3——同 blob 双算法键被误判"
         "「两代滞后」）。正法=①水位键一律 git show origin/main:<path> 原始 blob 直算（零树触碰·禁工作树/本地 "
         "commit 面）②键旁必标算法③origin tip 时间戳考古=本地面判别法（tip 未动而键变=本地面铁证）④内容消费"
         "回执与键修正同窗落地（本例 01..05 行已全在 origin blob=消费完整·回执保全）。How to apply：一切水位/"
         "内容寻址探针（decisions/orders/orders_ack 族）照此四步；跨机键交换先对算法再对值。"
         "| dept:工程 | r786 收口窗")

if not t.endswith(nl):
    t += nl
t += entry + nl
io.open(CP, "w", encoding="utf-8", newline="").write(t)
print("appended; size", len(t.encode("utf-8")))
