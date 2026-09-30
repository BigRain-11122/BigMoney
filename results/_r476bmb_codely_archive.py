import io, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '\\..')

hot = 'CODELY.md'
cold = os.path.join('research', 'memory-archive', '202609.md')

lines = io.open(hot, encoding='utf-8').read().split('\n')

# hot-cold: move self-describing cold-pointer lines (verbatim-duplicated in archive per their own text)
moved = [l for l in lines if l.startswith('- 冷层指针') and 'verbatim=archive' in l and len(l.encode('utf-8')) >= 500]
kept = [l for l in lines if l not in moved]

entry_a = ('- [2026-09-30 r476 bm-b] rebase 冲突停点 --amend=缝合提交坑+continue 幻影拒走正解（实弹）：停点 HEAD=onto 尖'
           '非被重放 pick，此窗 `git commit --amend` 会把上游他人轮提交改写成自家消息的缝合提交（本例吞 bm-c r284 '
           'closeout，幸未 push 零外溢）；PS5.1 `GIT_EDITOR=true git …`=bash 语法命令根本未跑=根因；'
           '`git rebase --continue --no-edit`=用法错 rc129。正解序列：停点只准 add+continue；幻影拒走（讨要消息）='
           '先 `git commit -m \'<原文>\'` 再裸 continue；要改消息=continue 完成后在分支尖 amend。姊妹面：冲突窗内 '
           'watchdog/autofill tick 可能把带冲突标记的共享库喂给 runner（本窗侥幸 tick 被重注册推迟）——长 rebase '
           '前先查下次点火时刻。')
entry_b = ('- [2026-09-30 r476 bm-b] 并发窗种子带撞号坑（exclusion_marginal_rand 20329000 实弹）：两机同窗独立选中'
           '同号——authoring 时点扫描零命中=假绿（对方冻结提交未落本地视野）；bm-c 先烧先发=保号既成事实，我方未烧='
           '让号改 20329500（registry 104 值扫描验空）。改号三同步面=registry 值+runner pin 断言与注释+pool '
           'data_gates 文本；prereg 不含具体值=零改。How to apply：种子零撞号扫描必须在 fetch/rebase 边界重跑，'
           'authoring 扫描不算数；撞号=未烧方让号勿争议，改号后 selftest 重验才收口。')

kept.append(entry_a)
kept.append(entry_b)
new_hot = '\n'.join(kept)
if not new_hot.endswith('\n'):
    new_hot += '\n'

with io.open(cold, 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n## CODELY 热冷整编 2026-09-30 r476 bm-b 窗批（指针行 verbatim 迁移，零丢失）\n\n')
    for l in moved:
        f.write(l + '\n')
    f.write('\n### 本窗新增坑律原行（热件同步留档）\n\n')
    f.write(entry_a + '\n')
    f.write(entry_b + '\n')

io.open(hot, 'w', encoding='utf-8', newline='\n').write(new_hot)

sz_hot = os.path.getsize(hot)
sz_moved = sum(len(l.encode('utf-8')) + 1 for l in moved)
print('moved pointer lines:', len(moved), 'bytes:', sz_moved)
print('CODELY.md new size:', sz_hot, '(hard line 10240:', 'UNDER' if sz_hot < 10240 else 'OVER', ')')
assert sz_hot < 10240, 'still over hard line'
# zero-loss verify: moved lines all present in cold file
cold_txt = io.open(cold, encoding='utf-8').read()
for l in moved:
    assert l in cold_txt, 'moved line missing in archive'
print('zero-loss verified: all moved lines present in archive 202609.md')
print('new entries present:', entry_a[:20] in io.open(hot, encoding='utf-8').read())
