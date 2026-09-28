# r369 bm-b: CODELY.md pitlaw append + batch-39 hot-cold archival (watermark law: append >10KB -> same-window)
# Laws: D-20260924-01, O-20260927-0230 (<=10KB hard line), batch-38 precedent (r392 bm-a).
# Zero-loss: archived entries byte-identical to removed hot lines (string equality assert).
import io

P_HOT = 'CODELY.md'
P_ARC = 'research/memory-archive/202609.md'

hot = io.open(P_HOT, encoding='utf-8').read()
lines = hot.split('\n')

r149 = [l for l in lines if l.startswith('- [2026-09-28 08:3x r149 bm-c]')]
r368 = [l for l in lines if l.startswith('- [2026-09-28 08:3x r368 bm-b]')]
assert len(r149) == 1 and len(r368) == 1, (len(r149), len(r368))
e149, e368 = r149[0], r368[0]

r369 = ("- [2026-09-28 08:4x r369 bm-b] 坑律：**S0 stash 活写进程的 tick/checkpoint 件后 rebase，pop 可撞活进程续写新面"
        "（would be overwritten）——判序=活面进度计数器 vs stash 时代进度，活面新者胜=stash 冗余可弃；弃置前活文件必过"
        "逐行解析+单调性完整性校验**（r369 实弹：w2b_checkpoint 经 S0 stash 后 pop 拒，活 census 进程已续写 i=2599 远超 "
        "stash 时代；逐行 2200/2200 JSON 解析+i 单调 PASS=checkout 替换与 open-handle append 竞态零孔洞 → drop stash "
        "保活面零丢失）。How to apply：rebase 前 stash tick 件即预期 pop 可撞车，撞车=比进度尾行（计数器/行数），"
        "活面≥stash→drop+完整性校验留痕；禁盲 force 覆活面、禁盲 stash apply 混双源。指针=本窗 stash 6793b0e0 drop 序。")

ptr39 = ("冷层指针：坑律正典 2026-09-28 三十九批（r369 bm-b 窗·水位律当窗整编：r369 新坑律 append 后超 ≤10KB 硬线）："
         "r149 bm-c rebase replay 未跟踪提取件挡 checkout / r368 bm-b rebase-continue EDITOR-unset 第三面 两条全文 "
         "verbatim=archive 202609.md『坑律归档 2026-09-28 三十九批』节（行级零丢失校验）。")

out = []
for l in lines:
    if l == e149 or l == e368:
        continue
    out.append(l)
    if l.startswith('冷层指针：坑律正典 2026-09-28 三十八批'):
        out.append(ptr39)
    if l.startswith('- [2026-09-28 08:2x r392 bm-a]'):
        out.append(r369)
new_hot = '\n'.join(out)
assert e149 not in new_hot and e368 not in new_hot
assert r369 in new_hot and ptr39 in new_hot
io.open(P_HOT, 'w', encoding='utf-8', newline='').write(new_hot)

arc = io.open(P_ARC, encoding='utf-8').read()
sec = ("\n\n## 坑律归档 2026-09-28 三十九批（r369 bm-b 窗·水位律当窗整编：r369 新坑律 append 后超 ≤10KB 硬线）\n\n"
       + e149 + "\n" + e368 + "\n")
assert e149 in sec and e368 in sec
io.open(P_ARC, 'a', encoding='utf-8', newline='').write(sec)

# zero-loss line-level verification: archived == removed, byte-identical
arc2 = io.open(P_ARC, encoding='utf-8').read()
assert e149 in arc2 and e368 in arc2, 'verbatim lost in archive'
hot2 = io.open(P_HOT, encoding='utf-8').read()
assert e149 not in hot2 and e368 not in hot2
import os
print('CODELY.md bytes:', os.path.getsize(P_HOT), '| >10KB:', os.path.getsize(P_HOT) > 10240)
print('archive bytes:', os.path.getsize(P_ARC))
print('zero-loss: r149+r368 verbatim in archive, removed from hot, r369+ptr39 landed')
