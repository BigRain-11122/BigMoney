# r427 bm-a CODELY hot/cold waterline reorg (r173 pattern) + batch-105 append
arc_path = 'research/memory-archive/202609.md'
hot_path = 'CODELY.md'
hot = open(hot_path, encoding='utf-8').read()
lines = hot.split('\n')
i102 = i103 = i104 = None
for i, ln in enumerate(lines):
    if ln.startswith('- [2026-09-29 11:5x r426 bm-a] 坑律一百零二批'):
        i102 = i
    if ln.startswith('- [2026-09-29 12:0x r215 bm-c'):
        i103 = i
    if ln.startswith('- [2026-09-29 12:1x r216 bm-c'):
        i104 = i
assert None not in (i102, i103, i104), (i102, i103, i104)
assert i103 == i102 + 1 and i104 == i103 + 1, 'contiguity check'
e102, e103 = lines[i102], lines[i103]
assert e102.endswith('禁 rebase-replay。') and e103.endswith('控制面 flip/finalize。'), 'entry integrity'
sec = '\n\n## 坑律归档 2026-09-29 r427 bm-a 窗批\n\n' + e102 + '\n' + e103 + '\n'
with open(arc_path, 'a', encoding='utf-8') as f:
    f.write(sec)
ptr = ('冷层指针（09-29 r427 bm-a 水位整编·r173 范式合并行·两行 verbatim 迁 archive 202609.md'
      '『坑律归档 2026-09-29 r427 bm-a 窗批』节·零删改）：坑律正典 2026-09-29 一百零二批'
      '（r426 bm-a·S0 rebase 队列构成诊断律·线性 rebase 静默丢未推 merge commit 坑）'
      '+一百零三批（r215 bm-c addendum 更新版·池条目 lane_owner 缺失死手窗+跨机数据面断言必查传输史）'
      '全文 verbatim=archive 对应节。')
b105 = ('- [2026-09-29 12:4x r427 bm-a] 坑律一百零五批（S0 脏树三步抢救律·stash-pop 撞头=正典可解面'
        '+untracked 撞转 tracked 静默不恢复处置律）：轮首脏树（崩溃轮 S6 遗产）pull --rebase 被 unstaged 拒'
        '→正解三步=git stash push -u→pull --rebase（快进面）→stash pop；pop 撞 UU=按冲突正典解'
        '（stash-pop 三 stage 与 rebase 同向：:2:=HEAD=origin 侧/:3:=stash=崩溃轮本地侧，'
        'merge_lane_views resolve 直用律成立；pop 后无 rebase 在飞=禁 rebase --continue，'
        'resolve 工具 next-hint 是 rebase 语境样板勿盲从）；untracked 件撞对岸同窗已 commit 同路径'
        '=pop 静默不恢复+stash 保留，处置=git show 双 blob 哈希+内容 diff（同批双机重跑收敛判定：'
        'checkpoint 逐字节恒等+verdict 唯一差异=generated 戳→证冗余 drop stash 零丢失；真分歧=保留+升级报告）。'
        'Why：崩溃轮遗产三态（tracked-mod/untracked/已被对岸落地）处置路径首次全走通。'
        'How to apply：S0 脏树一律三步法；pop 后逐件哈希比对再处置 stash；'
        'resolver 读 stage 用单冒号 f":{n}:{path}"（rev 串带尾冒号再拼=双冒号无效 revision 静默 None 坑·r427 实弹）。')
new_lines = []
for i, ln in enumerate(lines):
    if i in (i102, i103):
        continue
    new_lines.append(ln)
    if i == i104:
        new_lines.append(b105)
    if ln == '### Reference':
        new_lines.append(ptr)
new = '\n'.join(new_lines)
open(hot_path, 'w', encoding='utf-8', newline='').write(new)
arc = open(arc_path, encoding='utf-8').read()
assert e102 in arc and e103 in arc, 'archive zero-loss FAIL'
print('archive verbatim OK; hot size:', len(new.encode('utf-8')), 'B')
